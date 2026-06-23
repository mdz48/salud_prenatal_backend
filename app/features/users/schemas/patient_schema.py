from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.features.users.schemas.user_schema import UserCreate

class PatientBase(BaseModel):
    doctor_id: Optional[int] = None
    birthdate: date
    blood_type: Optional[str] | None = "O+"
    weeks_at_registration: Optional[int] = None
    last_menstrual_period: Optional[date] = None
    residence: str
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    height_cm: Optional[int] = None
    initial_weight: Optional[float] = None

class PatientCreate(PatientBase):
    user_id: int

class PatientUpdate(PatientBase):
    birthdate: Optional[date] = None

class PatientResponse(PatientBase):
    patient_id: int
    user_id: int
    current_gestational_weeks: int
    age: int

    model_config = ConfigDict(from_attributes=True)

class PatientRegistration(UserCreate, PatientBase):
    pass

class AppointmentDashboardResponse(BaseModel):
    appointment_id: int
    appointment_date: datetime
    status: str
    reason: Optional[str] = None
    doctor_name: str

    model_config = ConfigDict(from_attributes=True)

class PatientDashboardResponse(BaseModel):
    full_name: str
    current_gestational_weeks: Optional[int] = None
    current_doctor: Optional[str] = None
    current_doctor_image: Optional[str] = None
    current_doctor_specialty: Optional[str] = None
    upcoming_appointments: list[AppointmentDashboardResponse]

    model_config = ConfigDict(from_attributes=True)
