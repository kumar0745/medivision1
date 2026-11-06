from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import Base, engine
from .routers import auth, profile, dashboard, diagnosis, wellness, guidance, womens_health, emergency, assistant, reports
from . import models

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app=FastAPI(title=settings.app_name,version="1.0.0",description="MediVision AI academic healthcare wellness prototype. Not for clinical diagnosis.")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [auth.router,profile.router,dashboard.router,diagnosis.router,wellness.router,guidance.router,womens_health.router,emergency.router,assistant.router,reports.router]:
    app.include_router(router)

@app.get("/")
def root():
    return {"application":settings.app_name,"status":"running","docs":"/docs","safety":"Educational prototype; not a medical device."}
@app.get("/api/health")
def health():
    return {"status":"ok","application":settings.app_name,"version":"1.0.0","database":"configured"}
