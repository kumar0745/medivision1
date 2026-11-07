# MediVision AI test checklist

## Automated CI

- [ ] Backend tests: `cd backend && python -m pytest`
- [ ] Frontend production build: `cd frontend && npm run build`
- [ ] Playwright browser journeys: `cd frontend && npx playwright install chromium && npm run test:e2e`
- [ ] Backup crypto unit tests: `cd scripts && python -m pytest -q test_backup_crypto.py`

CI runs the backend tests, frontend build, browser journeys and backup crypto tests for PRs to main.

## Backend API journeys (synthetic data)

- [ ] Register with affirmative privacy consent; reject registration without consent.
- [ ] Sign in and confirm HttpOnly session cookie.
- [ ] Confirm account data is isolated between users.
- [ ] Confirm opt-in women's health endpoints reject users who have not opted in.
- [ ] Request password reset for a registered account and verify a generic response.
- [ ] Request password reset for an unknown account and verify the same generic response.
- [ ] Verify the reset token expires, is single-use, and previous sessions are invalidated after password change.
- [ ] Verify an email-delivery failure invalidates the token and does not disclose account existence.
- [ ] Reject uploads with unsupported types, invalid signatures, oversize files, missing scanner config, scanner outage and malware verdict.
- [ ] With ClamAV configured, allow only attachments receiving an explicit clean result.
- [ ] Verify attachment downloads require the owning user.
- [ ] Delete a test account and verify records, reset tokens, and attachments are removed.

## Browser journeys (Playwright)

- [ ] Explore the sample demo and move between Wellness and Profile.
- [ ] Register a synthetic user with explicit consent and reach the overview.
- [ ] Sign in with a mocked session response and reach the overview.
- [ ] Request a reset link and see the generic confirmation.
- [ ] Open a synthetic reset token in the URL fragment and submit a new password.

## Backup and restore

- [ ] Add the GitHub backup repository secrets/variables documented in `security-recovery-backups.md`.
- [ ] Run the encrypted backup workflow manually.
- [ ] Run the isolated restore-test workflow and confirm table counts and attachment hashes.
- [ ] Enable the daily workflow schedule only after the first successful backup and restore-test.
- [ ] Document a human-approved recovery plan before restoring any live branch.

## Remaining production gates

- [ ] Deploy and verify the private ClamAV service; until then, attachment uploads remain disabled.
- [ ] Configure and verify Resend sender credentials; until then, password-reset email is not sent.
- [ ] Add distributed/IP-based rate limiting for authentication.
- [ ] Complete independent security and privacy reviews, backup/restore exercise, retention review and legal assessment.
- [ ] Obtain clinical governance and independent validation before considering clinical decision support.

Do not use real patient data during testing.
