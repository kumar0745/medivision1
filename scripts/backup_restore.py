#!/usr/bin/env python3
"""Encrypted PostgreSQL + private attachment backups for MediVision.

Required environment:
  MEDIVISION_DATABASE_URL, RESTORE_TEST_DATABASE_URL (restore-test only)
  BACKUP_ENCRYPTION_PASSPHRASE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  AWS_ENDPOINT_URL_S3, AWS_REGION, BACKUP_BUCKET, SOURCE_BUCKET

PostgreSQL dumps are encrypted with GPG AES-256. Attachment objects and the manifest
are encrypted with AES-256-GCM before upload to a separate private bucket.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.config import Config
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from psycopg import connect, sql

MAGIC = b"MVAE1"
CHUNK_SIZE = 8 * 1024 * 1024


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=required("AWS_ENDPOINT_URL_S3"),
        region_name=required("AWS_REGION"),
        aws_access_key_id=required("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=required("AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.scrypt(passphrase.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)


def encrypt_envelope(plaintext: bytes, passphrase: str, associated_data: bytes) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    ciphertext = AESGCM(derive_key(passphrase, salt)).encrypt(nonce, plaintext, associated_data)
    return MAGIC + salt + nonce + ciphertext


def decrypt_envelope(envelope: bytes, passphrase: str, associated_data: bytes) -> tuple[bytes, bytes]:
    if len(envelope) < len(MAGIC) + 16 + 12 + 16 or not envelope.startswith(MAGIC):
        raise ValueError("Backup envelope has an unknown or truncated format.")
    offset = len(MAGIC)
    salt = envelope[offset:offset + 16]
    nonce = envelope[offset + 16:offset + 28]
    ciphertext = envelope[offset + 28:]
    plaintext = AESGCM(derive_key(passphrase, salt)).decrypt(nonce, ciphertext, associated_data)
    return plaintext, salt


def encrypt_object(plaintext: bytes, key: bytes, object_key: str) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, object_key.encode("utf-8"))


def decrypt_object(ciphertext: bytes, key: bytes, object_key: str) -> bytes:
    if len(ciphertext) < 28:
        raise ValueError(f"Encrypted attachment is truncated: {object_key}")
    return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], object_key.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def database_table_counts_from_connection(connection) -> dict[str, int]:
    result: dict[str, int] = {}
    rows = connection.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
    ).fetchall()
    for (table_name,) in rows:
        query = sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table_name))
        result[table_name] = connection.execute(query).fetchone()[0]
    return result


def database_table_counts(database_url: str) -> dict[str, int]:
    with connect(database_url) as connection:
        return database_table_counts_from_connection(connection)


def list_all_objects(client, bucket: str, prefix: str):
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            yield item


def backup():
    database_url = required("MEDIVISION_DATABASE_URL")
    passphrase = required("BACKUP_ENCRYPTION_PASSPHRASE")
    destination = required("BACKUP_BUCKET")
    source = required("SOURCE_BUCKET")
    client = s3_client()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prefix = f"database/{stamp}/"

    with tempfile.TemporaryDirectory(prefix="medivision-backup-") as temp:
        temp_dir = Path(temp)
        dump_path = temp_dir / "medivision.dump"
        encrypted_dump = temp_dir / "medivision.dump.gpg"
        passphrase_file = temp_dir / "gpg-passphrase"
        passphrase_file.write_text(passphrase, encoding="utf-8")
        passphrase_file.chmod(0o600)

        # Export one repeatable-read snapshot for both pg_dump and its table counts.
        # Keep this transaction open until pg_dump has imported the snapshot.
        with connect(database_url) as snapshot_connection:
            snapshot_connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            snapshot_id = snapshot_connection.execute("SELECT pg_export_snapshot()").fetchone()[0]
            table_counts = database_table_counts_from_connection(snapshot_connection)
            attachment_keys = [
                row[0] for row in snapshot_connection.execute(
                    "SELECT object_key FROM attachments ORDER BY object_key"
                ).fetchall()
            ]
            subprocess.run(
                ["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--compress=9",
                 "--snapshot", snapshot_id, "--file", str(dump_path), "--dbname", database_url],
                check=True,
            )
        subprocess.run(
            ["gpg", "--batch", "--yes", "--pinentry-mode", "loopback",
             "--passphrase-file", str(passphrase_file), "--symmetric",
             "--cipher-algo", "AES256", "--output", str(encrypted_dump), str(dump_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        encrypted_key = prefix + "medivision.dump.gpg"
        client.upload_file(str(encrypted_dump), destination, encrypted_key)

        salt = os.urandom(16)
        aes_key = derive_key(passphrase, salt)
        attachments = []
        for source_key in attachment_keys:
            response = client.get_object(Bucket=source, Key=source_key)
            body = response["Body"].read()
            stored_key = prefix + "attachments/" + source_key + ".aesgcm"
            encrypted = encrypt_object(body, aes_key, source_key)
            client.put_object(
                Bucket=destination,
                Key=stored_key,
                Body=encrypted,
                ContentType="application/octet-stream",
                Metadata={"source-sha256": hashlib.sha256(body).hexdigest()},
            )
            attachments.append({
                "source_key": source_key,
                "backup_key": stored_key,
                "sha256": hashlib.sha256(body).hexdigest(),
                "size_bytes": len(body),
                "content_type": response.get("ContentType", "application/octet-stream"),
            })

        manifest = {
            "format": "MediVision encrypted backup v1",
            "created_at": stamp,
            "database_dump_key": encrypted_key,
            "database_dump_sha256": sha256_file(dump_path),
            "database_table_counts": table_counts,
            "source_bucket": source,
            "backup_bucket": destination,
            "attachment_count": len(attachments),
            "source_attachment_count": len(attachment_keys),
            "attachments": attachments,
            "encryption": "GPG AES-256 for PostgreSQL; AES-256-GCM for attachments and manifest",
            "salt": base64.b64encode(salt).decode("ascii"),
        }
        manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
        manifest_key = prefix + "manifest.json.aesgcm"
        manifest_nonce = os.urandom(12)
        sealed_manifest = MAGIC + salt + manifest_nonce + AESGCM(aes_key).encrypt(
            manifest_nonce, manifest_bytes, b"manifest.json"
        )
        client.put_object(
            Bucket=destination,
            Key=manifest_key,
            Body=sealed_manifest,
            ContentType="application/octet-stream",
        )

    retention_days = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    stale_prefixes = set()
    for item in list_all_objects(client, destination, "database/"):
        key = item["Key"]
        parts = key.split("/")
        if len(parts) >= 2 and parts[1] < cutoff.strftime("%Y%m%dT%H%M%SZ"):
            stale_prefixes.add("/".join(parts[:2]) + "/")
    for stale in stale_prefixes:
        stale_objects = [x["Key"] for x in list_all_objects(client, destination, stale)]
        for start in range(0, len(stale_objects), 1000):
            client.delete_objects(Bucket=destination, Delete={
                "Objects": [{"Key": key} for key in stale_objects[start:start + 1000]],
                "Quiet": True,
            })
    print(json.dumps({
        "status": "complete",
        "backup_prefix": prefix,
        "attachment_count": len(attachments),
        "retention_days": retention_days,
    }))


def latest_manifest(client, bucket: str) -> tuple[str, dict, bytes]:
    keys = [x["Key"] for x in list_all_objects(client, bucket, "database/") if x["Key"].endswith("/manifest.json.aesgcm")]
    if not keys:
        raise RuntimeError("No complete backup manifest was found.")
    key = sorted(keys)[-1]
    passphrase = required("BACKUP_ENCRYPTION_PASSPHRASE")
    envelope = client.get_object(Bucket=bucket, Key=key)["Body"].read()
    plaintext, salt = decrypt_envelope(envelope, passphrase, b"manifest.json")
    manifest = json.loads(plaintext.decode("utf-8"))
    if manifest.get("format") != "MediVision encrypted backup v1":
        raise ValueError("Unsupported backup manifest format.")
    return key, manifest, salt


def restore_test():
    bucket = required("BACKUP_BUCKET")
    target_url = required("RESTORE_TEST_DATABASE_URL")
    passphrase = required("BACKUP_ENCRYPTION_PASSPHRASE")
    client = s3_client()
    _, manifest, salt = latest_manifest(client, bucket)
    aes_key = derive_key(passphrase, salt)

    with tempfile.TemporaryDirectory(prefix="medivision-restore-test-") as temp:
        temp_dir = Path(temp)
        encrypted_dump = temp_dir / "medivision.dump.gpg"
        dump_path = temp_dir / "medivision.dump"
        passphrase_file = temp_dir / "gpg-passphrase"
        passphrase_file.write_text(passphrase, encoding="utf-8")
        passphrase_file.chmod(0o600)

        client.download_file(bucket, manifest["database_dump_key"], str(encrypted_dump))
        subprocess.run(
            ["gpg", "--batch", "--yes", "--pinentry-mode", "loopback",
             "--passphrase-file", str(passphrase_file), "--decrypt",
             "--output", str(dump_path), str(encrypted_dump)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if sha256_file(dump_path) != manifest["database_dump_sha256"]:
            raise ValueError("PostgreSQL backup checksum validation failed.")

        subprocess.run(
            ["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-acl",
             "--exit-on-error", "--dbname", target_url, str(dump_path)],
            check=True,
        )

        actual_counts = database_table_counts(target_url)
        expected_counts = manifest["database_table_counts"]
        if actual_counts != expected_counts:
            raise ValueError(f"Restored table counts do not match backup. Expected {expected_counts}; got {actual_counts}.")

        verified_objects = 0
        for attachment in manifest["attachments"]:
            encrypted = client.get_object(Bucket=bucket, Key=attachment["backup_key"])["Body"].read()
            plain = decrypt_object(encrypted, aes_key, attachment["source_key"])
            if len(plain) != attachment["size_bytes"] or hashlib.sha256(plain).hexdigest() != attachment["sha256"]:
                raise ValueError(f"Attachment backup verification failed: {attachment['source_key']}")
            verified_objects += 1

    print(json.dumps({
        "status": "restore-test-passed",
        "database_tables": len(actual_counts),
        "database_table_counts": actual_counts,
        "attachments_verified": verified_objects,
        "backup_created_at": manifest["created_at"],
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["backup", "restore-test"])
    args = parser.parse_args()
    if args.command == "backup":
        backup()
    else:
        restore_test()
