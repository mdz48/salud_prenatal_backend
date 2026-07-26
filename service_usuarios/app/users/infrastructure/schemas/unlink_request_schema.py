from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal


class UnlinkRequestCreate(BaseModel):
    # El doctor NO se manda: se toma del vinculo vigente de la paciente.
    reason: Optional[str] = Field(default=None, max_length=500)


class ResolveUnlinkRequest(BaseModel):
    status: Literal["approved", "rejected"]


class UnlinkRequestResponse(BaseModel):
    unlink_request_id: int
    patient_id: int
    doctor_id: int
    status: str
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    patient_full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
