from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from app.core.enums import BloodTypeEnum
from .pregnancy_calculations import age_years, gestational_weeks
from .user_entity import UserEntity

class PatientEntity(BaseModel):
    patient_id: Optional[int] = None
    user_id: int
    doctor_id: Optional[int] = None
    birthdate: date
    blood_type: Optional[BloodTypeEnum] = None
    weeks_at_registration: Optional[int] = None
    last_menstrual_period: Optional[date] = None
    residence: str
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    height_cm: Optional[int] = None
    initial_weight: Optional[float] = None
    user: Optional[UserEntity] = None

    @property
    def current_gestational_weeks(self) -> int | None:
        return gestational_weeks(self.last_menstrual_period, self.weeks_at_registration)

    @property
    def age(self) -> int | None:
        return age_years(self.birthdate)

    model_config = ConfigDict(from_attributes=True)
