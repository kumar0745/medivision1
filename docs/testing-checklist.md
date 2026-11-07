# MediVision AI — testing checklist

## Interactive demo mode
- [ ] Sign-in screen opens and the demo entry action is visible.
- [ ] Demo opens without account registration.
- [ ] Demo data ribbon clearly identifies fictional sample data.
- [ ] Overview shows sample counts and recent records.
- [ ] Health note examples populate the input and save an additional demo record.
- [ ] Wellness mood, sleep and note inputs save and update the illustrative index.
- [ ] Age guidance checklist can be marked complete and incomplete.
- [ ] Women's health cycle note can be saved and appears in the history.
- [ ] Women's health awareness tab opens.
- [ ] Emergency contact can be added and deleted.
- [ ] Emergency text safety card downloads and states that contact details are not automatically shared.
- [ ] Assistant prompt buttons return an educational demo answer with references when relevant.
- [ ] My records shows sample entries and downloads a demo-labelled summary.
- [ ] Profile edits update the demo profile display.
- [ ] Reload preserves demo records in the same browser.
- [ ] Reset demo data restores the original sample set.
- [ ] Exit demo returns to sign-in.

## API-backed account mode
- [ ] Backend starts and /api/health returns status=ok.
- [ ] Swagger loads at /docs.
- [ ] User can register, log in and refresh the page.
- [ ] A second user cannot read the first user's records.
- [ ] Profile changes persist on the configured database.
- [ ] Health check saves a symptom note.
- [ ] Unsupported upload extension is rejected.
- [ ] Upload above configured size limit is rejected.
- [ ] Wellness check-in saves mood/sleep and returns a non-clinical illustrative index.
- [ ] Age-group guidance returns the expected content.
- [ ] Women's health routes require explicit opt-in.
- [ ] Cycle entry persists after opt-in.
- [ ] Emergency contact can be added and deleted.
- [ ] Assistant works in retrieval-only mode without an API key.
- [ ] Assistant sources are clickable.
- [ ] Summary export downloads account data.

## Implemented in production-hardening branch
- [x] Managed PostgreSQL and private object storage are configured in Vercel.
- [x] JWT key is rotated and stored encrypted.
- [x] Browser sessions use HttpOnly, Secure cookies; bearer tokens are not stored in localStorage.
- [x] Cookie-authenticated write requests check the allowed Origin.
- [x] Upload file type, signature and size are validated.
- [x] Attachment download checks account ownership and uses private storage.
- [x] Account deletion removes associated records and private attachments.
- [x] Health endpoint verifies a live database connection.
- [x] API tests and GitHub Actions quality checks added.

## Still required before handling real health information
- [ ] Run and review the CI test results and full production user-journey tests.
- [ ] Independent security assessment, threat model, penetration test and dependency audit.
- [ ] Malware scanning/quarantine for uploaded files.
- [ ] Distributed rate limiting and abuse protection.
- [ ] Email verification, password reset, MFA and session revocation.
- [ ] Versioned database migrations, backups and tested restore procedures.
- [ ] Audit trails, retention and independently verified data deletion.
- [ ] Privacy notice, consent language and jurisdiction-specific legal review.
- [ ] Clinical governance and validation before any clinical decision support.
- [ ] Verified emergency integrations and explicit user permissions.

## Explicitly not implemented
- No trained/validated medical image classifier.
- No definitive diagnosis or prescription.
- No validated clinical or mental-health risk score.
- No emergency dispatch or real-time location sharing.
- No claim of clinical validation.
