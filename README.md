# MediVision AI

**An Integrated AI-Based Healthcare Monitoring and Diagnosis Platform**

MediVision AI is an academic prototype that brings together health onboarding, preliminary health screening workflows, wellness tracking, age-aware exercise guidance, optional women's health tools, emergency information, and an AI health assistant.

> **Important medical safety notice:** This project is an educational prototype, not a medical device or clinical decision-support system. It does not provide definitive diagnoses, treatment recommendations, or emergency dispatch. Do not use it instead of a qualified healthcare professional or local emergency services. No clinical validation is claimed.

## Project modules
1. User onboarding and personalization.
2. AI diagnosis and health check intake workflows. **No trained/validated medical image classifier is included.**
3. Stress and mental wellness tracking.
4. Age-based general exercise and wellness guidance.
5. Optional women's health tracking and awareness.
6. Emergency information workflows. **No ambulance dispatch or verified live-location sharing integration is included.**
7. AI health assistant with a retrieval-oriented scaffold and optional LLM configuration.

## Technology
- Frontend: React, Vite, JavaScript, CSS
- Backend: Python, FastAPI
- Data layer: SQLAlchemy; SQLite by default, configurable database URL
- Assistant: retrieval service scaffold with optional LangChain/OpenAI configuration

## Structure
```text
backend/    FastAPI application, routers, models, services
frontend/   React/Vite client
docs/       Architecture, testing checklist, viva notes
```

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm

## Run locally

### Backend (PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
API: `http://127.0.0.1:8000`; interactive docs: `http://127.0.0.1:8000/docs`.

### Frontend (another PowerShell window)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Review `backend/.env.example` and `frontend/.env.example`. Put credentials only in ignored local `.env` files. Never commit API keys, passwords, tokens, patient data, or uploads.

## Current status and limitations
This repository is a starter prototype/scaffold, not a production-ready healthcare application. The image model is not trained or clinically validated; assistant output is informational and not a diagnosis; emergency workflows do not contact emergency services; real location sharing is not integrated. Authentication, authorization, privacy, secure deployment, logging, and data-retention controls need independent review before using real personal or patient data. Full end-to-end execution and frontend build have not been verified in this environment.

Use synthetic/demo data only. See `docs/` for architecture notes, testing checklist, and viva notes.

No license has been assigned yet; all rights reserved by default.
