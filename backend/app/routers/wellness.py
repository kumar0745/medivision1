from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, WellnessEntry
from ..schemas import WellnessIn

router = APIRouter(prefix="/api/wellness", tags=["Stress and wellness"])

@router.post("")
def create_entry(data: WellnessIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.mood not in ["Happy", "Normal", "Stressed", "Low", "Anxious"]:
        raise HTTPException(400, "Choose a valid mood.")
    sleep_factor = max(0, min(40, round(abs(8 - data.sleep_hours) * 8)))
    mood_factor = {"Happy": 5, "Normal": 15, "Stressed": 35, "Low": 40, "Anxious": 38}[data.mood]
    score = max(0, min(100, mood_factor + sleep_factor))
    row = WellnessEntry(user_id=user.id, mood=data.mood, sleep_hours=data.sleep_hours,
                        stress_score=score, note=data.note)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "mood": row.mood, "sleep_hours": row.sleep_hours, "stress_score": score,
            "suggestion": "Try a short grounding or breathing exercise. If distress is persistent or overwhelming, consider speaking with a qualified mental-health professional."}

@router.get("")
def list_entries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(WellnessEntry).filter_by(user_id=user.id).order_by(desc(WellnessEntry.created_at)).limit(60).all()
    return [{"id": r.id, "mood": r.mood, "sleep_hours": r.sleep_hours, "stress_score": r.stress_score,
             "note": r.note, "created_at": r.created_at} for r in rows]
