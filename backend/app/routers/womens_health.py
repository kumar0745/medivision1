from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, CycleEntry
from ..schemas import CycleIn

router = APIRouter(prefix="/api/womens-health", tags=["Women's health"])

def require_opt_in(user):
    if not user.women_health_opt_in:
        raise HTTPException(403, "Enable the optional women's health setting in your profile to use this private module.")

@router.post("/cycles")
def add_cycle(data: CycleIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_opt_in(user)
    row = CycleEntry(user_id=user.id, start_date=data.start_date, cycle_length=data.cycle_length, notes=data.notes)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "start_date": row.start_date, "cycle_length": row.cycle_length,
            "notice": "Cycle estimates are approximate and are not contraception or medical advice."}

@router.get("/cycles")
def get_cycles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_opt_in(user)
    rows = db.query(CycleEntry).filter_by(user_id=user.id).order_by(desc(CycleEntry.created_at)).limit(24).all()
    return [{"id": r.id, "start_date": r.start_date, "cycle_length": r.cycle_length,
             "notes": r.notes, "created_at": r.created_at} for r in rows]

@router.get("/awareness")
def awareness(user: User = Depends(get_current_user)):
    require_opt_in(user)
    return {"topics": [
        {"title": "Cycle patterns", "text": "Track dates and symptoms; patterns differ from person to person."},
        {"title": "PCOS awareness", "text": "Irregular cycles, acne or excess hair can have several causes. No online score can diagnose PCOS; a clinician can assess symptoms and tests."},
        {"title": "Pregnancy wellness", "text": "For pregnancy-specific advice, consult an obstetric professional. Seek urgent care for concerning symptoms."}
    ], "notice": "Private educational information, not diagnosis or treatment."}
