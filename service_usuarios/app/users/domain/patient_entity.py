from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from salud_prenatal_shared_core.pregnancy_calculations import age_years
from .user_entity import UserEntity

class PatientEntity(BaseModel):
    patient_id: Optional[int] = None
    user_id: int
    doctor_id: Optional[int] = None
    birthdate: date
    linked_at: Optional[datetime] = None
    user: Optional[UserEntity] = None

    @property
    def age(self) -> int | None:
        return age_years(self.birthdate)

    model_config = ConfigDict(from_attributes=True)
