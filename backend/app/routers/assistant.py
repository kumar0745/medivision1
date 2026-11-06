from fastapi import APIRouter, Depends
from ..core.security import get_current_user
from ..models.user import User
from ..schemas import ChatIn
from ..services.assistant import answer_question

router=APIRouter(prefix="/api/assistant",tags=["AI health assistant"])
@router.post("/chat")
async def chat(data:ChatIn,user:User=Depends(get_current_user)):
    result=await answer_question(data.message)
    result["notice"]="Educational support only; not a diagnosis, prescription, or emergency service."
    return result
