# MediVision AI — production-hardening release

## Changes in this release

- Requires PostgreSQL, a non-default 32+ character signing secret, explicit CORS origins and S3-compatible private storage when ENVIRONMENT=production.
- Uses a 45-minute access-token lifetime by default.
- Uses HttpOnly, Secure, SameSite=Lax browser session cookies. The frontend does not store access tokens in localStorage.
- Routes browser API requests through a same-origin Vercel `/api/*` rewrite to keep session cookies first-party.
- Checks the Origin header on cookie-authenticated write requests.
- Stores uploaded attachments under opaque per-user object keys in private S3 storage; downloads require the owning account and use a 60-second signed URL.
- Validates upload extensions, file signatures and maximum size before storage.
- Adds attachment metadata (owner, record, content type, size and SHA-256 checksum) in PostgreSQL.
- Adds account deletion, including deletion of private attachments and associated records.
- Adds response security headers and restricts API CORS methods and headers.
- Health checks execute SELECT 1 and return HTTP 503 when the database is unavailable.
- Adds API tests and a GitHub Actions quality workflow.
- Adds account deletion controls and protected attachment download actions to the web UI.

## Production environment variables

Configure these only in the backend Vercel project's encrypted environment-variable store. Never put credentials in GitHub or frontend Vite variables.

- ENVIRONMENT=production
- DATABASE_URL (Neon pooled PostgreSQL URL)
- SECRET_KEY (random, unique, 32+ characters)
- FRONTEND_ORIGINS (exact HTTPS frontend origins, comma-separated)
- STORAGE_BACKEND=s3
- S3_BUCKET=health-attachments
- AWS_ENDPOINT_URL_S3, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

The frontend Vercel project's `VITE_API_URL=/` makes the API client use relative `/api` paths, which are rewritten by `frontend/vercel.json` to the backend project.

## Deployment notes

The signing secret has been rotated. This intentionally invalidates tokens signed with the previous key; users must sign in again.

This release adds an attachments table. The backend startup creates this new table via SQLAlchemy metadata. Future schema changes should use reviewed, versioned migrations rather than relying on create_all.

The prior temporary SQLite database did not provide durable storage and was not migrated. Existing temporary records are not available in the new persistent database; users need to create accounts again.

## Remaining work before handling real health information

- Independent application-security review and penetration test.
- Deploy the private ClamAV service and configure `MALWARE_SCANNER_URL` and `MALWARE_SCANNER_TOKEN`; uploads are fail-closed until this is done.
- Configure GitHub backup secrets/variables, run the encrypted backup, pass the isolated restore-test, then enable its daily schedule. Neon scheduled snapshots are not enabled on this project plan.
- Configure Resend sender/API credentials for the implemented 30-minute single-use password reset flow; add email verification, MFA and distributed abuse/rate limiting.
- Privacy notice, consent language and jurisdiction-specific legal review.
- Clinical governance and independent validation before adding diagnostic or decision-support models.
- Operational monitoring, alerting, support ownership, incident response and disaster recovery.
- Do not claim HIPAA, DPDP, ISO 27001 or clinical compliance based only on this code release.

MediVision remains a personal wellness and health-education prototype, not a medical device, diagnostic service or emergency dispatch platform.


See [Security, recovery and backups](security-recovery-backups.md) for the integration setup and test instructions.
