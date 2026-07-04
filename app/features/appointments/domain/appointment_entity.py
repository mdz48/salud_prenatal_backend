from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import AppointmentStatusEnum

class AppointmentEntity(BaseModel):
    appointment_id: Optional[int] = None
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    status: AppointmentStatusEnum = AppointmentStatusEnum.pending
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
