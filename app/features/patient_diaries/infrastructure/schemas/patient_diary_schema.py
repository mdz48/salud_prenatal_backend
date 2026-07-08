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
    weight_gain: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ExtractedSymptomResponse(BaseModel):
    code: str
    label: Optional[str] = None
    raw_text: Optional[str] = None
    negated: bool = False
    score: Optional[float] = None
    alarm: bool = False

    model_config = ConfigDict(from_attributes=True)
