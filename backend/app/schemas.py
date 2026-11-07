from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    age: Optional[int] = Field(default=None, ge=16, le=120)
    age_group: str = "30-45"
    gender: Optional[str] = Field(default=None, max_length=40)
    health_goal: str = Field(default="prevent", max_length=80)
    women_health_opt_in: bool = False
    privacy_consent: bool = False

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: Optional[int] = Field(default=None, ge=16, le=120)
    age_group: str
    gender: Optional[str] = Field(default=None, max_length=40)
    health_goal: str = Field(max_length=80)
    women_health_opt_in: bool = False

class DiagnosisIn(BaseModel):
    symptoms: str = Field(min_length=3, max_length=3000)
    category: str = Field(default="symptom-check", max_length=50)

class WellnessIn(BaseModel):
    mood: str = Field(max_length=30)
    sleep_hours: float = Field(ge=0, le=24)
    note: Optional[str] = Field(default=None, max_length=1000)

class CycleIn(BaseModel):
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    cycle_length: int = Field(default=28, ge=15, le=60)
    notes: Optional[str] = Field(default=None, max_length=500)

class ContactIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    relationship: str = Field(min_length=2, max_length=50)
    phone: str = Field(min_length=7, max_length=30)

class ChatIn(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
