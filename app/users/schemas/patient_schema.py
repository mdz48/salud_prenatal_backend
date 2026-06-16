from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    doctor_id: Optional[int] = None
    birthdate: date
    blood_type: Optional[str] = None
    weeks_at_registration: Optional[int] = None
    last_menstrual_period: Optional[date] = None
    previous_hypertension: Optional[bool] = None
    diabetes: Optional[bool] = None
    family_history_hypertension: Optional[bool] = None
    previous_pregnancies: Optional[bool] = None
    previous_deliveries: Optional[bool] = None
    previous_miscarriages: Optional[bool] = None
    previous_cesareans: Optional[bool] = None
    previous_preeclampsia: Optional[bool] = None
    chronic_kidney_disease: Optional[bool] = None
    chronic_hypertension: Optional[bool] = None
    multiple_pregnancy: Optional[bool] = None
    fetal_death: Optional[bool] = None
    fetal_growth_restriction: Optional[bool] = None
    family_history_heart_disease: Optional[bool] = None

class PatientCreate(PatientBase):
    user_id: int

class PatientUpdate(PatientBase):
    birthdate: Optional[date] = None

class PatientResponse(PatientBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
