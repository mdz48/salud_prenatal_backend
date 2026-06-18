from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from app.features.users.schemas.user_schema import UserCreate
from app.features.medical_record.schemas.medical_record_schema import MedicalRecordBase, MedicalRecordResponse

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
    medical_record: Optional[MedicalRecordBase] = None
