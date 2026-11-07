# MediVision AI
**An AI-Assisted Personal Wellness and Health-Education Platform**

MediVision AI is a responsive academic prototype for personal wellness organisation and health education. It combines onboarding, health-note capture, self-reported wellness tracking, age-group guidance, opt-in women's health tracking, emergency preparedness, a source-linked health assistant, and personal summaries.

> **Medical safety:** This is an educational prototype, not a medical device or clinical decision-support system. It does not provide definitive diagnosis, treatment or emergency dispatch. Do not use it instead of a qualified healthcare professional or local emergency services. No clinical validation is claimed.

## Explore the interactive demo

Open the deployed website and choose **Explore interactive demo** on the sign-in screen. No registration is required.

The demo contains fictional sample data for wellness check-ins, personal health notes, women's health cycle entries and a clearly-marked example emergency contact. You can create additional test entries, explore suggestions, download a sample summary and reset the data from the sidebar.

- Demo entries are saved in the current browser's `localStorage`.
- Demo mode does not send entries to the API or a healthcare professional.
- The demo contact uses a dummy number and is not a real person.
- Use the sidebar's **Reset demo data** action to restore the sample values.
- Demo data is not shared between browsers or devices.

## Modules

1. **Onboarding and personalisation** — account registration/login, age group, optional demographic fields, wellness goal and explicit women's health opt-in.
2. **Health check and note capture** — symptom descriptions, guided examples, record categories and optional attachment name; this prototype does not analyse uploaded images.
3. **Stress and mental wellness** — mood and sleep check-ins, personal notes, an illustrative index, recent history and a gentle breathing prompt.
4. **Age-based wellness guidance** — general ideas for age groups 16–30, 30–45 and 45+, with a tappable routine checklist.
5. **Women's health** — opt-in cycle log and general awareness information; no PCOS or pregnancy diagnosis.
6. **Emergency preparedness** — emergency contact list, safety checklist and downloadable personal safety card. The call link opens the device dialler; it is not an automated dispatch integration.
7. **AI health assistant** — guided prompts, simple-language educational responses and reference links. Demo mode uses fixed example responses; account mode uses the backend retrieval assistant.
8. **Personal records** — health-note history and downloadable wellness summary.
9. **Profile and preferences** — update profile and optional modules.

## Technology

- Frontend: React, Vite, JavaScript, CSS and Lucide icons
- Backend: Python and FastAPI
- Database layer: SQLAlchemy; SQLite locally by default, PostgreSQL URL supported
- Assistant: curated retrieval service with optional LangChain/OpenAI configuration
- Hosting: Vercel frontend and FastAPI projects connected to GitHub

## Repository structure

```text
backend/
  app/
    core/           configuration, database, security
    models/         SQLAlchemy data models
    routers/        auth, profile, dashboard, diagnosis, wellness,
                    guidance, women's health, emergency, assistant, reports
    services/       assistant and curated knowledge retrieval
  index.py          Vercel FastAPI entry point
  requirements.txt
frontend/
  src/
    App.jsx         responsive UI and demo mode
    styles.css      pastel responsive styling
    services/api.js API client and session handling
  index.html
  package.json
docs/
  architecture.md
  demo-mode.md
  testing-checklist.md
  release-checklist.md
  viva-notes.md
```

## Quality checks

Run the backend checks from `backend/`:

```powershell
python -m pip install -r requirements.txt
pytest
```

Build the frontend from `frontend/`:

```powershell
npm install
npm run build
```

GitHub Actions runs both checks for the production-hardening branch and pull requests.

See [production readiness notes](docs/production-readiness.md) for deployment configuration and remaining launch work.

## Run locally (Windows PowerShell)

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`  
Swagger docs: `http://127.0.0.1:8000/docs`

### Frontend (open another PowerShell window)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

Set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env` when the API is hosted separately.

## Vercel deployment

The GitHub repository is connected to two Vercel projects:

- **Frontend:** project root directory `frontend`, Vite build, output `dist`.
- **Backend:** project root directory `backend`, FastAPI entry point `index.py`.

The frontend uses a same-origin `/api/*` rewrite to the backend, preserving first-party HttpOnly cookies. The backend uses `FRONTEND_ORIGINS` to allow trusted browser origins.

### Production infrastructure

The production-hardening branch is configured for:

- Managed PostgreSQL on Neon (Singapore region) for persistent account and wellness records.
- A private Neon Object Storage bucket for attachments. Files use opaque, per-user object keys; download access is checked against the signed-in owner and uses a short-lived URL.
- A rotated JWT signing key stored as an encrypted Vercel environment variable.
- HttpOnly, Secure, SameSite=Lax browser session cookies; the frontend no longer keeps access tokens in localStorage. A same-origin Vercel `/api` rewrite keeps the cookie first-party.
- Explicit CORS allow-list and origin checks on cookie-authenticated write requests.
- File extension, size and signature checks before storage; attachments are not analyzed for diagnosis.
- A database health check that executes a real `SELECT 1` query.
- Account deletion for the user's records and stored attachments.
- Backend API tests, Playwright browser journeys, encrypted backup/restore tooling and GitHub Actions quality checks.

Never put database credentials, OpenAI keys, JWT secrets, passwords, patient records or uploaded files in GitHub. Store production secrets only in encrypted deployment environment variables. The frontend must never contain a private API key.

The backend's previous temporary SQLite data was not migrated. Users need to create a new account on the persistent database.

## Environment variables

Backend variables are documented in `backend/.env.example`. Important values:

- `SECRET_KEY`: a strong, unique secret for signing tokens.
- `DATABASE_URL`: local SQLite or a managed PostgreSQL connection string.
- `FRONTEND_ORIGINS`: comma-separated allowed frontend origins.
- `UPLOAD_DIR`: local development storage path. Production files use private object storage.
- `MALWARE_SCANNER_URL` / `MALWARE_SCANNER_TOKEN`: required to enable file attachments after a clean ClamAV verdict.
- `APP_BASE_URL`, `RESEND_API_KEY`, `EMAIL_FROM`: required to send account-recovery email.
- `OPENAI_API_KEY`: optional server-side assistant key; do not expose this to Vite.

Frontend:

- `VITE_API_URL`: the API base URL. It is public configuration, not a secret.

## Current limitations and safe use

- No trained or clinically validated medical image classifier is included. Uploaded files are not diagnosed.
- The wellness index is a simple illustrative calculation, not a validated mental-health or clinical score.
- Exercise guidance is general information, not medical clearance.
- Women's health tools are opt-in awareness and record-keeping only.
- Emergency routes do not dispatch ambulances or share live location.
- Demo assistant responses are scripted educational examples. Account assistant responses use a curated local retrieval library and optional LLM configuration.
- Demo sample data is fictional and browser-local.
- Production data uses managed Neon PostgreSQL and private Neon Object Storage. Upload scanning and email recovery remain disabled until their external services are configured. Do not use real patient or sensitive health data until the remaining security, privacy and clinical reviews are complete.
- Authentication, authorisation, privacy, security, retention, monitoring and clinical governance need independent review before any real-world deployment.

See `docs/` for the architecture, demo guide, testing checklist, release checklist, [security/recovery/backup setup](docs/security-recovery-backups.md), and viva notes.

No license has been assigned; all rights reserved by default.
