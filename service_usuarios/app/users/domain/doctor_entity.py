from pydantic import BaseModel, ConfigDict
from typing import Optional

class DoctorEntity(BaseModel):
    doctor_id: Optional[int] = None
    user_id: int
    professional_license: Optional[str] = None
    specialty: Optional[str] = None
    office: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
