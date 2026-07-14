from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ReceptionistInfo(BaseModel):
    user_id: int
    name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    receptionist_id: Optional[int] = None
    receptionist: Optional[ReceptionistInfo] = None
    subscription_status: Optional[str] = None
