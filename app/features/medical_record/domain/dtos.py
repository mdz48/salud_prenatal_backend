from typing import Optional
from pydantic import BaseModel


class PatientInfo(BaseModel):
    patient_id: Optional[int] = None
    user_id: int
    name: str
    last_name: str
    current_gestational_weeks: Optional[int]
    age: Optional[int]
    doctor_id: Optional[int] = None
    birthdate: Optional[str] = None
    residence: Optional[str] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    height_cm: Optional[int] = None
    initial_weight: Optional[float] = None
    blood_type: Optional[str] = None
