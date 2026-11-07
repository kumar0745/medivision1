from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from .core.config import settings
from .core.database import Base, engine
from .routers import auth, profile, dashboard, diagnosis, wellness, guidance, womens_health, emergency, assistant, reports
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.1.0",
    description="MediVision AI wellness and health-education prototype. Not for clinical diagnosis.",
    docs_url="/docs" if settings.environment.lower() != "production" else None,
    redoc_url="/redoc" if settings.environment.lower() != "production" else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def security_headers_and_csrf(request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in settings.origins:
            return JSONResponse(status_code=403, content={"detail": "Request origin is not trusted."})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/")
def root():
    return {"application": settings.app_name, "status": "running",
            "safety": "Educational prototype; not a medical device."}

@app.get("/api/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database is unavailable.")
    return {"status": "ok", "application": settings.app_name, "version": "1.1.0",
            "database": "connected", "storage": settings.storage_backend}
