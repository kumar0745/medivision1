from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..models.user import User
from ..schemas import RegisterIn, LoginIn

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def public_user(user):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "age": user.age,
            "age_group": user.age_group, "gender": user.gender, "health_goal": user.health_goal,
            "women_health_opt_in": user.women_health_opt_in}

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if not data.privacy_consent:
        raise HTTPException(400, "Privacy consent is required to create an account.")
    if data.age_group not in ["16-30", "30-45", "45+"]:
        raise HTTPException(400, "Choose a valid age group.")
    user = User(full_name=data.full_name.strip(), email=data.email.lower(),
                password_hash=hash_password(data.password), age=data.age, age_group=data.age_group,
                gender=data.gender, health_goal=data.health_goal,
                women_health_opt_in=data.women_health_opt_in, privacy_consent=data.privacy_consent)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with this email already exists.")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user": public_user(user)}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password.")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user": public_user(user)}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return public_user(user)
