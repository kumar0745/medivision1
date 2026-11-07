# MediVision security, account recovery and backup release

## Account recovery

- Request route: `POST /api/auth/forgot-password`.
- Reset route: `POST /api/auth/reset-password`.
- Reset tokens are generated with cryptographic randomness, stored only as SHA-256 hashes, expire in 30 minutes, and are single-use.
- Previous unconsumed links are invalidated when a newer reset link is requested.
- The request endpoint returns the same generic 202 message for registered and unknown emails.
- A maximum of three reset requests per user per hour is applied. Use a WAF or distributed rate limiter for IP-level abuse controls.
- Password changes invalidate existing sessions: signed JWTs carry a fingerprint of the current password hash, checked on every authenticated request.
- The token is placed in the URL fragment (`#reset_token=...`), which is not sent in HTTP requests or normal referrer headers.
- Email delivery uses Resend. A verified sender/domain is required.

### Configure password-reset email in backend Vercel

Set these environment variables for the backend project:

- `APP_BASE_URL=https://medivision1-web.vercel.app`
- `RESEND_API_KEY` (encrypted secret from your Resend account)
- `EMAIL_FROM` (a sender address/domain verified in Resend)

Until all three values are configured, the endpoint returns the non-enumerating generic response but does not send email. The health endpoint reports `password_reset_email: not_configured`.

## Malware scanning

The backend checks extension, file signature and size, then sends bytes to a separate authenticated scanner service before storage.

- Scanner code: `scanner/`.
- Runtime: Docker image with ClamAV daemon and freshclam signature updates.
- Scanner health: `GET /health`; it reports ready only after clamd answers `PING`.
- Scan route: authenticated `POST /scan`; accepts raw bytes and returns `{"clean":true,"engine":"ClamAV"}` only on a ClamAV clean response.
- Infected content is rejected with HTTP 422.
- A missing, unavailable or inconclusive scanner is HTTP 503. Attachments are not persisted unless a clean verdict is returned.
- The service is not deployed by the Vercel frontend/backend projects. It needs a private container host reachable from the FastAPI backend. Keep the service private, TLS-protected, and allow only the backend to call it.

### Configure the scanner

Build and deploy `scanner/Dockerfile` to a private container platform. Provide the scanner container with a unique `SCANNER_TOKEN` of at least 32 random characters. Set these backend Vercel variables:

- `MALWARE_SCANNER_URL` (private HTTPS base URL of the scanner, no trailing path)
- `MALWARE_SCANNER_TOKEN` (same token used by the scanner, encrypted)

Until both backend variables are set and the scanner is healthy, attachment uploads remain disabled. Health reports `malware_scanning: disabled_fail_closed` when not configured. Health configuration status is not a substitute for a successful scan; the scan request itself must return a clean verdict.

Do not point the backend at an untrusted/public scanner endpoint. The scanner handles private user-uploaded files.

## Database and attachment backups

A private Neon Object Storage bucket named `medivision-backups` has been created on the production database branch. A manual Neon snapshot already exists:

- Snapshot: `medivision-pre-recovery-drill-2026-11-07`
- Snapshot ID: `snap-calm-mountain-az1ww3f1`
- Source branch: production `main`

Neon automated backup schedules are not enabled for this project plan, and the one manual snapshot quota is currently occupied. The GitHub backup workflow therefore provides an independent encrypted export/restore-test path.

### Backup format

`scripts/backup_restore.py`:

- Exports PostgreSQL in custom format with `pg_dump`.
- Encrypts the database dump with GPG AES-256.
- Copies every attachment from `health-attachments` to `medivision-backups`, encrypted client-side with AES-256-GCM.
- Writes an encrypted manifest with table counts, object names, object sizes and SHA-256 hashes.
- Removes backup prefixes older than 30 days after a new successful backup.
- Restore-test decrypts to a temporary PostgreSQL 17 database, runs `pg_restore`, compares row counts and verifies all attachment checksums without writing to the live database or source attachment bucket.

The backup job uses an isolated runner and never writes unencrypted dump files to the repository or artifacts. Temporary plaintext dump and GPG passphrase files live only in the runner's temporary directory and are deleted at job end.

### Configure GitHub Actions secrets and variables

Open the repository in GitHub:

**Settings → Secrets and variables → Actions**

Create these repository secrets:

| Secret | Purpose |
|---|---|
| `MEDIVISION_DATABASE_URL` | Neon pooled PostgreSQL connection string for the production database |
| `BACKUP_ENCRYPTION_PASSPHRASE` | A unique, high-entropy passphrase used to derive AES-256-GCM keys and encrypt the dump |
| `MEDIVISION_BACKUP_AWS_ACCESS_KEY_ID` | Neon Object Storage access credential for the production branch |
| `MEDIVISION_BACKUP_AWS_SECRET_ACCESS_KEY` | Matching Neon Object Storage secret |

Create these repository variables:

| Variable | Value |
|---|---|
| `MEDIVISION_BACKUP_S3_ENDPOINT` | `https://br-snowy-shape-az5vg024.storage.c-3.ap-southeast-1.aws.neon.tech` |
| `MEDIVISION_BACKUP_S3_REGION` | `ap-southeast-1` |

The Neon credential must allow storage read/write for the production branch and both private buckets. Create it in the Neon console and copy the credential values directly to GitHub Secrets; do not paste these credentials into this chat or commit them. The database URL and passphrase are also secrets and must not be stored as GitHub variables.

After setting those values, open **Actions → MediVision encrypted backup and restore → Run workflow**:

1. Run `backup` and verify a successful backup prefix is printed.
2. Run `restore-test` to restore into the isolated PostgreSQL 17 CI service and verify table counts and attachment hashes.

The workflow is manual-only until these credentials have been added and a successful run has been verified. Once verified, add the daily schedule trigger to `.github/workflows/backup-restore.yml` (currently omitted so the repository does not generate predictable failed scheduled runs before setup). The sample schedule is `30 20 * * *` UTC, or 02:00 IST.

A restore-test is non-destructive to production. Do not restore a snapshot or database dump onto the live branch without a reviewed incident/recovery plan and an explicit operator decision.

## Test coverage

The CI quality workflow now includes:

- Backend API tests for authentication, account isolation, recovery tokens, reset token reuse, old-session revocation, file signature checks, fail-closed scanning and attachment ownership.
- Frontend production build.
- Playwright browser journeys for demo navigation, sign-in, registration with consent, forgot-password and reset-password screens.
- Unit tests for backup encryption/decryption, wrong passphrases and attachment key binding.

The browser tests use synthetic data and mocked API responses. They do not register accounts in the production database or exercise the real Resend/ClamAV integrations.

## Still required before real health-data use

- Configure and independently validate the private scanner host and Resend sender.
- Add IP-level distributed rate limiting for authentication endpoints.
- Configure GitHub backup secrets/variables, run a real backup, and successfully run a restore-test.
- Enable a daily workflow schedule after initial backup/restore validation.
- Perform a security review, privacy/legal review, recovery exercise and clinical governance review.
- Define retention/deletion policies for database backups and attachments, and document any legal hold requirements.

This release does not establish regulatory compliance, clinical validation, or suitability for real patient records.
