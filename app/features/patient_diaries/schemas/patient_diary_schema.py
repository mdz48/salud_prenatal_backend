from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PatientDiaryBase(BaseModel):
    medical_record_id: int
    weight_kg: Optional[float] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None

class PatientDiaryCreate(PatientDiaryBase):
    pass

class PatientDiaryUpdate(BaseModel):
    weight_kg: Optional[float] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None

class PatientDiaryResponse(PatientDiaryBase):
    patient_diary_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
