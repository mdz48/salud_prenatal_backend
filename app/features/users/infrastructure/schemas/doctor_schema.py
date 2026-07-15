from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from app.features.users.infrastructure.schemas.user_schema import UserCreate
from app.features.users.infrastructure.schemas.receptionist_schema import ReceptionistResponse

class DoctorBase(BaseModel):
    professional_license: Optional[str] = Field(None, max_length=255)
    specialty: Optional[str] = Field(None, max_length=100)
    office: Optional[str] = Field(None, max_length=255)

class DoctorCreate(DoctorBase):
    user_id: int

class DoctorUpdate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    doctor_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class DoctorRegistration(UserCreate, DoctorBase):
    pass

class DoctorDetailResponse(DoctorBase):
    doctor_id: int
    user_id: int
    name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DoctorTodayAppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    appointment_time: datetime
    reason: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class DoctorDashboardResponse(BaseModel):
    receptionists: List[ReceptionistResponse]
    today_appointments_count: int
    today_appointments: List[DoctorTodayAppointmentResponse]

    model_config = ConfigDict(from_attributes=True)
