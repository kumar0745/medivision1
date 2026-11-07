import pytest

from backup_restore import (
    decrypt_envelope,
    decrypt_object,
    encrypt_envelope,
    encrypt_object,
)


def test_manifest_envelope_round_trip():
    source = b'{"backup":"synthetic"}'
    sealed = encrypt_envelope(source, "test-only-passphrase", b"manifest.json")
    plaintext, salt = decrypt_envelope(sealed, "test-only-passphrase", b"manifest.json")
    assert plaintext == source
    assert len(salt) == 16


def test_manifest_envelope_rejects_wrong_passphrase():
    sealed = encrypt_envelope(b"private", "right-passphrase", b"manifest.json")
    with pytest.raises(Exception):
        decrypt_envelope(sealed, "wrong-passphrase", b"manifest.json")


def test_manifest_authentication_rejects_wrong_context():
    sealed = encrypt_envelope(b"private", "test-passphrase", b"manifest.json")
    with pytest.raises(Exception):
        decrypt_envelope(sealed, "test-passphrase", b"other-manifest.json")


def test_attachment_encryption_round_trip_and_key_binding():
    source = b"synthetic attachment bytes"
    sealed = encrypt_object(source, b"k" * 32, "users/7/synthetic.png")
    assert decrypt_object(sealed, b"k" * 32, "users/7/synthetic.png") == source
    with pytest.raises(Exception):
        decrypt_object(sealed, b"k" * 32, "users/8/synthetic.png")
