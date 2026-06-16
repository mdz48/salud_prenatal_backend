from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.enums import RoleEnum

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    role: RoleEnum = RoleEnum.patient
    is_active: bool = True
    image_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)