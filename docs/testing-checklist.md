# MediVision AI — Testing checklist

## Local smoke test
- [ ] Backend starts and /api/health returns status=ok.
- [ ] Swagger loads at /docs.
- [ ] User can register, log in, and refresh the page without losing the session.
- [ ] A second user cannot read the first user's records.
- [ ] Profile changes persist after reload.
- [ ] Health check saves a symptom note.
- [ ] Unsupported upload extension is rejected.
- [ ] Upload above configured size limit is rejected.
- [ ] Wellness check-in saves mood/sleep and returns a non-clinical stress index.
- [ ] Age-group guidance returns the expected content.
- [ ] Women's health routes require opt-in.
- [ ] Cycle entry persists after opt-in.
- [ ] Emergency contact can be added and deleted.
- [ ] Assistant works in retrieval-only mode without an API key.
- [ ] Assistant sources are clickable.
- [ ] Summary export downloads a text file.
- [ ] Frontend production build completes.

## Before real-world deployment
- [ ] Threat model, penetration test, dependency audit.
- [ ] HTTPS, strict CORS, rate limiting and abuse protection.
- [ ] Production JWT secret rotation.
- [ ] Encryption at rest and in transit; secure key management.
- [ ] Malware scanning and MIME/content validation for uploads.
- [ ] Audit trails, retention, deletion and backup restore tests.
- [ ] Privacy/legal review for applicable health-data requirements.
- [ ] Clinical governance and validation before any clinical decision support.
- [ ] Verified emergency integrations and explicit user permissions.
