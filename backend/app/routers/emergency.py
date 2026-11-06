from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, EmergencyContact
from ..schemas import ContactIn

router=APIRouter(prefix="/api/emergency",tags=["Emergency preparedness"])
@router.post("/contacts")
def add_contact(data: ContactIn,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    count=db.query(EmergencyContact).filter_by(user_id=user.id).count()
    if count>=5: raise HTTPException(400,"You can save up to five emergency contacts.")
    row=EmergencyContact(user_id=user.id,name=data.name,relationship=data.relationship,phone=data.phone)
    db.add(row);db.commit();db.refresh(row)
    return {"id":row.id,"name":row.name,"relationship":row.relationship,"phone":row.phone}
@router.get("/contacts")
def list_contacts(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    rows=db.query(EmergencyContact).filter_by(user_id=user.id).all()
    return [{"id":r.id,"name":r.name,"relationship":r.relationship,"phone":r.phone} for r in rows]
@router.get("/summary")
def summary(user:User=Depends(get_current_user)):
    return {"name":user.full_name,"age":user.age,"age_group":user.age_group,"health_goal":user.health_goal,
            "emergency_notice":"This summary is user-entered profile information and may be incomplete. Verify it before sharing."}
@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    row=db.query(EmergencyContact).filter_by(id=contact_id,user_id=user.id).first()
    if not row: raise HTTPException(404,"Contact not found")
    db.delete(row);db.commit();return {"message":"Contact deleted"}
