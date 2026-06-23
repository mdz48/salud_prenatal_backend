from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class MedicalRecordBase(BaseModel):
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
    active_smoking: Optional[bool] = None

class MedicalRecordCreate(MedicalRecordBase):
    patient_id: int
    doctor_id: int

class MedicalRecordResponse(MedicalRecordBase):
    medical_record_id: int
    patient_id: int
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)

class ConsultationSummary(BaseModel):
    consultation_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PatientMedicalRecordResponse(BaseModel):
    user_id: int
    name: str
    last_name: str
    current_gestational_weeks: Optional[int] = None
    age: Optional[int] = None
    medical_record: Optional[MedicalRecordResponse] = None
    consultations: List[ConsultationSummary]
    risk_prediction: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
