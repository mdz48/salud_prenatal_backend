from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import List, Optional

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

class ReceptionistDetailResponse(BaseModel):
    receptionist_id: int
    user_id: int
    doctor_id: int
    name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class ReceptionistAppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    appointment_time: datetime
    reason: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class ReceptionistDashboardResponse(BaseModel):
    full_name: str
    upcoming_appointments: List[ReceptionistAppointmentResponse]
    pending_appointments: List[ReceptionistAppointmentResponse]
    confirmed_appointments: List[ReceptionistAppointmentResponse]

    model_config = ConfigDict(from_attributes=True)
