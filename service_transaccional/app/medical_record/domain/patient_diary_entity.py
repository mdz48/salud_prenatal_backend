from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PatientDiaryEntity(BaseModel):
    patient_diary_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    weight_kg: Optional[float] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    weight_gain: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True, extra="allow")
