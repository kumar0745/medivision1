from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, WellnessEntry, DiagnosisRecord, CycleEntry

router=APIRouter(prefix="/api/reports",tags=["Reports"])
@router.get("/summary")
def report(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    wellness=db.query(WellnessEntry).filter_by(user_id=user.id).order_by(desc(WellnessEntry.created_at)).limit(10).all()
    checks=db.query(DiagnosisRecord).filter_by(user_id=user.id).order_by(desc(DiagnosisRecord.created_at)).limit(10).all()
    return {"generated_for":user.full_name,"profile":{"age_group":user.age_group,"health_goal":user.health_goal},
            "wellness":[{"mood":w.mood,"sleep_hours":w.sleep_hours,"stress_score":w.stress_score,"date":w.created_at} for w in wellness],
            "health_checks":[{"symptoms":d.symptoms,"guidance":d.guidance,"date":d.created_at} for d in checks],
            "disclaimer":"Personal wellness summary only. Not a medical record, diagnosis, or substitute for clinician review."}
@router.get("/summary.txt",response_class=PlainTextResponse)
def download_summary(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    data=report(db,user)
    lines=["MEDIVISION AI — PERSONAL WELLNESS SUMMARY","",f"Name: {data['generated_for']}",f"Age group: {data['profile']['age_group']}",f"Health goal: {data['profile']['health_goal']}","","WELLNESS CHECK-INS"]
    for w in data["wellness"]:
        lines.append(f"{w['date']}: mood={w['mood']}, sleep={w['sleep_hours']}h, stress index={w['stress_score']}/100")
    lines += ["","HEALTH CHECK NOTES"]
    for d in data["health_checks"]:
        lines += [f"{d['date']}: {d['symptoms']}",d["guidance"],""]
    lines += ["",data["disclaimer"]]
    return "\n".join(lines)
