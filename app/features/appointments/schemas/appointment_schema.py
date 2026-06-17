from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from app.core.enums import AppointmentStatusEnum

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = Field(None, max_length=255)

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatusEnum] = None
    reason: Optional[str] = Field(None, max_length=255)

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
