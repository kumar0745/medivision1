import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.config import settings
from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..core.file_storage import delete_file
from ..core.email import send_password_reset_email
from ..models.user import (
    User, DiagnosisRecord, Attachment, WellnessEntry, CycleEntry,
    EmergencyContact, PasswordResetToken,
)
from ..schemas import RegisterIn, LoginIn, ForgotPasswordIn, ResetPasswordIn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
RESET_GENERIC = "If an account exists for that email, a password-reset link will be sent."


def public_user(user):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "age": user.age,
            "age_group": user.age_group, "gender": user.gender, "health_goal": user.health_goal,
            "women_health_opt_in": user.women_health_opt_in}


def set_session_cookie(response: Response, token: str):
    response.set_cookie(
        key="mv_session", value=token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True, secure=settings.environment.lower() == "production",
        samesite="lax", path="/",
    )


def clear_session_cookie(response: Response):
    response.delete_cookie(
        key="mv_session", path="/",
        httponly=True, secure=settings.environment.lower() == "production",
        samesite="lax",
    )


@router.post("/register")
def register(data: RegisterIn, response: Response, db: Session = Depends(get_db)):
    if not data.privacy_consent:
        raise HTTPException(400, "Privacy consent is required to create an account.")
    if data.age_group not in ["16-30", "30-45", "45+"]:
        raise HTTPException(400, "Choose a valid age group.")
    user = User(full_name=data.full_name.strip(), email=str(data.email).strip().lower(),
                password_hash=hash_password(data.password), age=data.age, age_group=data.age_group,
                gender=data.gender, health_goal=data.health_goal,
                women_health_opt_in=data.women_health_opt_in, privacy_consent=True)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with this email already exists.")
    set_session_cookie(response, create_access_token(str(user.id), user.password_hash))
    return {"token_type": "cookie", "user": public_user(user)}


@router.post("/login")
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(data.email).strip().lower()).first()
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password.")
    set_session_cookie(response, create_access_token(str(user.id), user.password_hash))
    return {"token_type": "cookie", "user": public_user(user)}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(data: ForgotPasswordIn, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()

    # The response is identical for unknown accounts, disabled delivery, and throttled requests.
    if not user or not settings.email_configured:
        return {"message": RESET_GENERIC}

    now = datetime.now(timezone.utc)
    recent_count = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.created_at >= now - timedelta(hours=1),
    ).count()
    if recent_count >= 3:
        return {"message": RESET_GENERIC}

    raw_token = secrets.token_urlsafe(36)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now}, synchronize_session=False)
    token_row = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=now + timedelta(minutes=30),
    )
    db.add(token_row)
    db.commit()

    reset_url = f"{settings.app_base_url.rstrip('/')}/#reset_token={quote(raw_token, safe='')}"
    try:
        send_password_reset_email(user.email, reset_url)
    except Exception:
        logger.warning("Password-reset email could not be delivered; request remains undisclosed.")
        token_row.used_at = now
        db.commit()
    return {"message": RESET_GENERIC}


@router.post("/reset-password")
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    token_row = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now,
    ).first()
    if not token_row:
        raise HTTPException(400, "This password-reset link is invalid or has expired. Request a new link.")

    user = db.query(User).filter(User.id == token_row.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(400, "This password-reset link is invalid or has expired. Request a new link.")

    # Updating the password hash invalidates every previously issued JWT for this account.
    user.password_hash = hash_password(data.password)
    token_row.used_at = now
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.id != token_row.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now}, synchronize_session=False)
    db.commit()
    return {"message": "Password updated. Sign in with your new password."}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    clear_session_cookie(response)
    return response


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return public_user(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attachments = db.query(Attachment).filter_by(user_id=user.id).all()
    try:
        for item in attachments:
            delete_file(item.object_key)
    except Exception:
        raise HTTPException(503, "Account files could not be securely removed. Please retry.")

    db.query(PasswordResetToken).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.query(Attachment).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.query(DiagnosisRecord).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.query(WellnessEntry).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.query(CycleEntry).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.query(EmergencyContact).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_session_cookie(response)
    return response
