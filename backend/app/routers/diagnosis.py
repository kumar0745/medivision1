from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import settings
from ..models.user import User, DiagnosisRecord
from ..schemas import DiagnosisIn

router = APIRouter(prefix="/api/diagnosis", tags=["Health check"])
ALLOWED = {".png",".jpg",".jpeg",".webp",".pdf"}
URGENT_TERMS = ["chest pain","difficulty breathing","shortness of breath","face drooping","weakness on one side","unconscious","severe bleeding","suicidal"]

def build_guidance(symptoms: str):
    lower = symptoms.lower()
    if any(term in lower for term in URGENT_TERMS):
        severity = "Urgent attention"
        message = ("Your description includes a symptom that can sometimes signal an emergency. "
                   "Do not rely on this tool. Seek urgent medical help now through your local emergency number or nearest emergency department.")
    else:
        severity = "Needs review"
        message = ("This prototype cannot identify a disease or determine clinical severity. Record when symptoms started, "
                   "what makes them better or worse, and any associated symptoms. Arrange advice from a qualified healthcare professional, "
                   "especially if symptoms persist, worsen, or concern you.")
    return severity, message + " This is general safety guidance, not a diagnosis."

@router.post("")
async def create_check(symptoms: str = Form(...), category: str = Form("symptom-check"),
                       file: UploadFile | None = File(default=None),
                       db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if len(symptoms.strip()) < 3 or len(symptoms) > 3000:
        raise HTTPException(400, "Please enter between 3 and 3000 characters.")
    saved_name = None
    if file:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED:
            raise HTTPException(415, "Allowed file types: PNG, JPG, WEBP, PDF.")
        content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"File must be under {settings.max_upload_mb} MB.")
        if not content:
            raise HTTPException(400, "Uploaded file is empty.")
        upload_dir = Path(settings.upload_dir); upload_dir.mkdir(parents=True, exist_ok=True)
        saved_name = f"{uuid4().hex}{ext}"
        (upload_dir / saved_name).write_bytes(content)
    severity, guidance = build_guidance(symptoms)
    row = DiagnosisRecord(user_id=user.id, symptoms=symptoms.strip(), category=category,
                          attachment_name=(file.filename[:250] if file else None), guidance=guidance, severity=severity)
    db.add(row); db.commit(); db.refresh(row)
    return {"id":row.id,"severity":severity,"guidance":guidance,"created_at":row.created_at,
            "attachment_received":bool(saved_name),"medical_notice":"No image model is enabled. Upload is stored as a record only; no image diagnosis is performed."}

@router.get("")
def list_checks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(DiagnosisRecord).filter_by(user_id=user.id).order_by(desc(DiagnosisRecord.created_at)).limit(50).all()
    return [{"id":r.id,"symptoms":r.symptoms,"category":r.category,"severity":r.severity,"guidance":r.guidance,"attachment_name":r.attachment_name,"created_at":r.created_at} for r in rows]
