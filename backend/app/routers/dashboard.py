from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, WellnessEntry, DiagnosisRecord, CycleEntry

router = APIRouter(prefix="/api", tags=["Dashboard"])
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wellness = db.query(WellnessEntry).filter_by(user_id=user.id).order_by(desc(WellnessEntry.created_at)).first()
    diagnoses = db.query(DiagnosisRecord).filter_by(user_id=user.id).order_by(desc(DiagnosisRecord.created_at)).limit(5).all()
    cycles = db.query(CycleEntry).filter_by(user_id=user.id).order_by(desc(CycleEntry.created_at)).limit(3).all()
    return {
        "user":{"full_name":user.full_name,"age_group":user.age_group,"health_goal":user.health_goal},
        "latest_wellness": None if not wellness else {"mood":wellness.mood,"sleep_hours":wellness.sleep_hours,"stress_score":wellness.stress_score,"created_at":wellness.created_at},
        "diagnosis_count":db.query(DiagnosisRecord).filter_by(user_id=user.id).count(),
        "wellness_count":db.query(WellnessEntry).filter_by(user_id=user.id).count(),
        "recent_records":[{"id":r.id,"symptoms":r.symptoms[:110],"severity":r.severity,"created_at":r.created_at} for r in diagnoses],
        "cycle_tracking_enabled":user.women_health_opt_in,
        "cycle_count":len(cycles)
    }
