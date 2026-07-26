from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class InvitationCodeEntity(BaseModel):
    invitation_code_id: Optional[int] = None
    code: str
    doctor_id: int
    is_used: bool = False
    expires_at: datetime
    created_at: Optional[datetime] = None
    used_by_patient_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
