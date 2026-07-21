from pydantic import BaseModel
from typing import Optional

class DeviceTokenCreate(BaseModel):
    token: str
    device_type: Optional[str] = "android"

class DeviceTokenUnregister(BaseModel):
    token: str

class PatientLinkedEventRequest(BaseModel):
    patient_id: int
    doctor_id: int
