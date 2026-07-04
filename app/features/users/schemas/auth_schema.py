from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
