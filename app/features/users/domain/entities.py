from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date, datetime
from typing import Optional
from app.core.enums import RoleEnum, BloodTypeEnum

class UserEntity(BaseModel):
    user_id: Optional[int] = None
    name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: RoleEnum = RoleEnum.patient
    is_active: bool = True
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DoctorEntity(BaseModel):
    doctor_id: Optional[int] = None
    user_id: int
    professional_license: Optional[str] = None
    specialty: Optional[str] = None
    office: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

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

    @property
    def current_gestational_weeks(self) -> int | None:
        if self.last_menstrual_period:
            delta = date.today() - self.last_menstrual_period
            return delta.days // 7
        return self.weeks_at_registration

    @property
    def age(self) -> int | None:
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

    model_config = ConfigDict(from_attributes=True)

class ReceptionistEntity(BaseModel):
    receptionist_id: Optional[int] = None
    user_id: int
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)

class InvitationCodeEntity(BaseModel):
    invitation_code_id: Optional[int] = None
    code: str
    doctor_id: int
    is_used: bool = False
    expires_at: datetime
    created_at: Optional[datetime] = None
    used_by_patient_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
