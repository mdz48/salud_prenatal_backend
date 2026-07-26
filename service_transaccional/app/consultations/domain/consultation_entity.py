from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConsultationEntity(BaseModel):
    consultation_id: Optional[int] = None
    medical_record_id: int
    notes: Optional[str] = None
    objective: Optional[str] = None
    plan: Optional[str] = None
    reported_facts: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
