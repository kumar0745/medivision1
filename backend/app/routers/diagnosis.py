from pathlib import Path
from hashlib import sha256
import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import settings
from ..core.file_storage import store_file, signed_download_url, local_file_path
from ..models.user import User, DiagnosisRecord, Attachment

router = APIRouter(prefix="/api/diagnosis", tags=["Health check"])
ALLOWED = {
    ".png": ("image/png", lambda b: b.startswith(bytes([137, 80, 78, 71, 13, 10, 26, 10]))),
    ".jpg": ("image/jpeg", lambda b: b.startswith(bytes([255, 216, 255]))),
    ".jpeg": ("image/jpeg", lambda b: b.startswith(bytes([255, 216, 255]))),
    ".webp": ("image/webp", lambda b: len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
    ".pdf": ("application/pdf", lambda b: b.startswith(b"%PDF-")),
}
URGENT_TERMS = ["chest pain", "difficulty breathing", "shortness of breath", "face drooping",
                "weakness on one side", "unconscious", "severe bleeding", "suicidal"]


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


def scan_uploaded_file(content: bytes) -> None:
    if not settings.scanner_configured:
        raise HTTPException(503, "Secure file scanning is not configured. Attachments are temporarily disabled.")
    try:
        response = httpx.post(
            settings.malware_scanner_url.rstrip("/") + "/scan",
            content=content,
            headers={"Authorization": f"Bearer {settings.malware_scanner_token}",
                     "Content-Type": "application/octet-stream"},
            timeout=25.0,
        )
    except httpx.HTTPError:
        raise HTTPException(503, "The malware scanner is unavailable. No attachment was saved.")
    if response.status_code == 422:
        raise HTTPException(422, "This attachment was blocked by the malware scanner.")
    if response.status_code != 200:
        raise HTTPException(503, "The malware scanner could not verify this attachment.")
    try:
        verdict = response.json()
    except ValueError:
        raise HTTPException(503, "The malware scanner returned an invalid response.")
    if verdict.get("clean") is not True or verdict.get("engine") != "ClamAV":
        raise HTTPException(503, "The malware scanner did not confirm this attachment is clean.")


@router.post("")
async def create_check(symptoms: str = Form(...), category: str = Form("symptom-check"),
                       file: UploadFile | None = File(default=None),
                       db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    clean_symptoms = symptoms.strip()
    if len(clean_symptoms) < 3 or len(clean_symptoms) > 3000:
        raise HTTPException(400, "Please enter between 3 and 3000 characters.")
    if len(category) > 50:
        raise HTTPException(400, "Invalid record category.")

    content = extension = content_type = filename = None
    if file:
        filename = Path(file.filename or "attachment").name[:255]
        extension = Path(filename).suffix.lower()
        allowed = ALLOWED.get(extension)
        if not allowed:
            raise HTTPException(415, "Allowed file types: PNG, JPG, WEBP, PDF.")
        content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"File must be under {settings.max_upload_mb} MB.")
        if not content:
            raise HTTPException(400, "Uploaded file is empty.")
        content_type, signature_check = allowed
        if not signature_check(content):
            raise HTTPException(415, "The uploaded file content does not match its extension.")
        scan_uploaded_file(content)

    object_key = None
    if content is not None:
        try:
            object_key = store_file(user.id, extension, content, content_type)
        except Exception:
            raise HTTPException(503, "Secure file storage is temporarily unavailable. No record was saved.")

    severity, guidance = build_guidance(clean_symptoms)
    row = DiagnosisRecord(user_id=user.id, symptoms=clean_symptoms, category=category,
                          attachment_name=filename, guidance=guidance, severity=severity)
    try:
        db.add(row)
        db.flush()
        if object_key:
            db.add(Attachment(user_id=user.id, diagnosis_record_id=row.id, object_key=object_key,
                              original_filename=filename, content_type=content_type,
                              size_bytes=len(content), sha256=sha256(content).hexdigest()))
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        if object_key:
            try:
                from ..core.file_storage import delete_file
                delete_file(object_key)
            except Exception:
                pass
        raise HTTPException(500, "The health note could not be saved. Please retry.")

    return {"id": row.id, "severity": severity, "guidance": guidance, "created_at": row.created_at,
            "attachment_received": bool(object_key),
            "medical_notice": "Uploads are stored as private attachments only. Files are scanned before storage; no image diagnosis is performed."}


@router.get("/{record_id}/attachment")
def download_attachment(record_id: int, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    attachment = db.query(Attachment).join(
        DiagnosisRecord, Attachment.diagnosis_record_id == DiagnosisRecord.id
    ).filter(
        Attachment.diagnosis_record_id == record_id,
        Attachment.user_id == user.id,
        DiagnosisRecord.user_id == user.id,
    ).first()
    if not attachment:
        raise HTTPException(404, "Attachment not found.")
    if settings.storage_backend.lower() == "s3":
        return RedirectResponse(signed_download_url(attachment.object_key), status_code=302)
    path = local_file_path(attachment.object_key)
    if not path.is_file():
        raise HTTPException(404, "Attachment file is missing.")
    return FileResponse(path, media_type=attachment.content_type,
                        filename=attachment.original_filename, content_disposition_type="attachment")


@router.get("")
def list_checks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(DiagnosisRecord).filter_by(user_id=user.id).order_by(
        desc(DiagnosisRecord.created_at)
    ).limit(50).all()
    return [{"id": r.id, "symptoms": r.symptoms, "category": r.category, "severity": r.severity,
             "guidance": r.guidance, "attachment_name": r.attachment_name, "created_at": r.created_at}
            for r in rows]
