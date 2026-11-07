# MediVision AI — release and demonstration checklist

## Frontend
- [ ] Sign-in screen renders.
- [ ] Interactive demo opens without creating an account.
- [ ] Mobile navigation opens and closes.
- [ ] Overview cards and navigation cards work.
- [ ] Demo data ribbon is visible in demo mode.
- [ ] Reset demo data restores sample values.
- [ ] Demo mode remains usable after refresh in the same browser.
- [ ] Demo sample data is not shown in a normal account session.
- [ ] Forms have labels, hints and suggested examples.
- [ ] Save actions show feedback.
- [ ] Summary and safety-card exports download.
- [ ] Frontend build completes.

## API-backed account mode
- [ ] Register a synthetic test account.
- [ ] Log in and refresh the page.
- [ ] Profile update persists on the configured backend.
- [ ] Create and list a health note.
- [ ] Create and list a wellness check-in.
- [ ] Age guidance loads for all supported age groups.
- [ ] Women's health endpoint requires explicit opt-in.
- [ ] Add and delete an emergency contact.
- [ ] Assistant returns educational content and source links.
- [ ] Summary export returns account data.
- [ ] Verify one account cannot access another account's records.

## Deployment and data
- [ ] Frontend and backend Vercel builds are READY.
- [ ] Frontend and API domains return HTTP 200.
- [ ] API CORS allows the deployed frontend origin.
- [ ] JWT signing key is unique and encrypted in Vercel.
- [ ] Replace temporary `/tmp` SQLite with managed PostgreSQL.
- [ ] Replace temporary upload storage with private durable object storage.
- [ ] Configure backups, deletion, retention and audit logging.
- [ ] Add production monitoring and error alerting.
- [ ] Complete security, privacy and clinical governance review before using real health data.

## Explicit non-goals
- No diagnosis from uploaded medical images.
- No validated clinical risk or mental-health score.
- No medication prescribing.
- No ambulance dispatch or verified live-location sharing.
- No clinical validation claim.
