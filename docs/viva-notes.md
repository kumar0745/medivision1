# MediVision AI — Viva notes

## Project objective
MediVision AI is a personal wellness and health-information prototype that brings together user onboarding, symptom note capture, wellness check-ins, age-aware general activity guidance, optional women's health tracking, emergency preparedness, and a retrieval-grounded health information assistant.

## Why this project?
Health information and personal wellness activity are often fragmented across separate applications. This prototype offers one place to organize user-entered wellness information and access general educational references.

## Architecture
React provides the responsive interface. FastAPI exposes REST endpoints. SQLAlchemy maps application data to SQLite by default and PostgreSQL optionally. JWT protects account-specific endpoints. A small curated retrieval library grounds assistant responses; OpenAI is optional and accessed only by the backend.

## What is AI in this prototype?
The assistant can retrieve relevant reference snippets and, if configured, use a language model to explain them in plain language. This is not an AI diagnostic model. No trained medical image classifier is included, and uploaded images are stored only as attachments associated with a health note.

## Key limitations
The prototype is not clinically validated, does not diagnose or prescribe, does not provide medical clearance, and does not contact emergency services. Its wellness stress index is a simple illustrative indicator, not a validated mental-health score.

## Future scope
- Add clinician-reviewed datasets and validated models under formal clinical governance.
- Add FHIR-compatible interoperability with authorized healthcare systems.
- Add secure object storage, encryption, audit events and granular consent.
- Add verified telehealth/hospital/ambulance integrations.
- Add localization, voice accessibility and offline support.
