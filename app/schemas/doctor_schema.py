from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class DoctorBase(BaseModel):
    professional_license: Optional[str] = Field(None, max_length=255)
    specialty: Optional[str] = Field(None, max_length=100)
    office: Optional[str] = Field(None, max_length=255)

class DoctorCreate(DoctorBase):
    user_id: int

class DoctorUpdate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
