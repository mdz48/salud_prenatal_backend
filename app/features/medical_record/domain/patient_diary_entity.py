from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PatientDiaryEntity(BaseModel):
    patient_diary_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, extra="allow")
