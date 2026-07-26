from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class ConsultationBase(BaseModel):
    medical_record_id: int
    notes: Optional[str] = Field(None, max_length=255)
    objective: Optional[str] = Field(None, max_length=255)
    plan: Optional[str] = Field(None, max_length=255)
    reported_facts: str = Field(..., max_length=255)

class ConsultationCreate(ConsultationBase):
    pass

class ConsultationResponse(ConsultationBase):
    consultation_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
