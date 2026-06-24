from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ReceptionistCreate(BaseModel):
    name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = Field(None, max_length=20)

class ReceptionistResponse(BaseModel):
    user_id: int
    name: str
    last_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
