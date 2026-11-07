# MediVision AI
**An Integrated AI-Based Healthcare Monitoring and Diagnosis Platform**

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

The frontend has `VITE_API_URL` set to the backend domain. The backend uses `FRONTEND_ORIGINS` to allow the frontend origin.

### Important storage limitation

The current Vercel backend is configured with a temporary SQLite database at `/tmp/medivision.db` and temporary upload storage at `/tmp/medivision-uploads`. **Vercel function instances can be replaced, so this storage is not durable.** Account registrations, records and uploads may be lost. Connect a managed PostgreSQL database and durable object storage before expecting persistent accounts or real-world use.

Never put database credentials, OpenAI keys, JWT secrets, passwords, patient records or uploaded files in GitHub. Add production secrets only through Vercel's Environment Variables interface. The frontend must never contain a private API key.

## Environment variables

Backend variables are documented in `backend/.env.example`. Important values:

- `SECRET_KEY`: a strong, unique secret for signing tokens.
- `DATABASE_URL`: local SQLite or a managed PostgreSQL connection string.
- `FRONTEND_ORIGINS`: comma-separated allowed frontend origins.
- `UPLOAD_DIR`: local or temporary upload directory.
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
- The current Vercel database and file storage are temporary. Do not use real patient or sensitive health data.
- Authentication, authorisation, privacy, security, retention, monitoring and clinical governance need independent review before any real-world deployment.

See `docs/` for the architecture, demo guide, testing checklist, release checklist and viva notes.

No license has been assigned; all rights reserved by default.
