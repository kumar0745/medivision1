from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas import ProfileUpdate
from .auth import public_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])
@router.get("")
def get_profile(user: User = Depends(get_current_user)):
    return public_user(user)

@router.put("")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    for key, value in data.model_dump().items():
        setattr(user, key, value)
    db.commit(); db.refresh(user)
    return public_user(user)
