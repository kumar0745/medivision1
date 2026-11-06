from fastapi import APIRouter, Depends, HTTPException
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/guidance", tags=["Age-based guidance"])
GUIDES = {
 "16-30":{"title":"Build strong foundations","items":["Mix enjoyable cardio with age-appropriate strength work.","Take movement breaks during long study or screen sessions.","Keep a consistent sleep routine and hydration habits.","Use gradual progression; avoid exercising through pain."]},
 "30-45":{"title":"Balance work and wellbeing","items":["Break up long sitting periods with short movement breaks.","Try gentle neck, shoulder, back and eye-rest routines.","Make time for regular activity, recovery and sleep.","Track relevant health measurements with clinician guidance."]},
 "45+":{"title":"Move steadily and safely","items":["Choose comfortable walking, balance and mobility activities.","Begin at a manageable level and increase gradually.","Use support or supervision if balance is uncertain.","Ask a clinician about activity changes if you have chronic conditions or new symptoms."]}
}
@router.get("/{age_group}")
def guidance(age_group: str, user: User = Depends(get_current_user)):
    if age_group not in GUIDES: raise HTTPException(404,"Unknown age group")
    return {**GUIDES[age_group],"notice":"General wellness education only. This is not a personal exercise clearance or a guarantee of safety."}
