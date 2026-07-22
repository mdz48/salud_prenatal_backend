from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.users.infrastructure.schemas.user_schema import UserCreate

class PatientBase(BaseModel):
    # Patient es relacional + identidad. Lo clinico vive en el expediente.
    doctor_id: Optional[int] = None
    birthdate: date

class PatientCreate(PatientBase):
    user_id: int

class PatientUpdate(PatientBase):
    birthdate: Optional[date] = None

class PatientResponse(PatientBase):
    patient_id: int
    user_id: int
    full_name: Optional[str] = None
    current_gestational_weeks: Optional[int] = None
    age: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PatientRegistration(UserCreate, PatientBase):
    pass

class PatientSearchResult(BaseModel):
    patient_id: int
    user_id: int
    name: str
    last_name: str
    age: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PatientDirectoryEntry(BaseModel):
    patient_id: int
    user_id: int
    doctor_id: Optional[int] = None
    linked_at: Optional[datetime] = None
    age: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

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
