# MediVision AI — Architecture

## Overview
The React/Vite client communicates with a FastAPI REST backend. SQLAlchemy maps user and health records to SQLite by default; PostgreSQL can be configured through the database URL. The backend exposes modular routers for authentication, profiles, dashboard, screening intake, wellness, guidance, women's health, emergency contacts, assistant, and reports.

## Data boundaries
Account-specific records are scoped to the authenticated user. Passwords are hashed and bearer tokens protect account routes. OpenAI credentials are configured on the server and must never be placed in frontend code. Uploaded files are stored privately as attachments; the current project does not send them to a trained image diagnosis model.

## Feature mapping
- Onboarding and profile: users table
- Symptom/image intake: diagnosis_records
- Stress and wellness: wellness_entries
- Age-group guidance: static general guidance content
- Women's health: cycle_entries, gated by explicit opt-in
- Emergency preparedness: emergency_contacts and safety information
- Assistant: curated retrieval references and optional server-side OpenAI invocation
- Reports: account-scoped personal summary export

## Safety and privacy
This is an academic prototype, not a medical device. Do not use real patient data. Before production, add threat modelling, access-control testing, encryption, audit trails, retention/deletion controls, monitoring, backups, privacy/legal review, and clinical governance.
