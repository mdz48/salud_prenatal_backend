from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from app.core.enums import BloodTypeEnum
from app.features.patient_diaries.infrastructure.schemas.patient_diary_schema import AggregatedSymptomResponse

class MedicalRecordBase(BaseModel):
    # Perfil clinico (capturado por el doctor al crear/editar el expediente)
    blood_type: Optional[BloodTypeEnum] = None
    weeks_at_registration: Optional[int] = None
    last_menstrual_period: Optional[date] = None
    residence: Optional[str] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    height_cm: Optional[int] = None
    initial_weight: Optional[float] = None
    initial_systolic: Optional[int] = None
    initial_diastolic: Optional[int] = None

    previous_hypertension: Optional[bool] = None
    diabetes: Optional[bool] = None
    family_history_hypertension: Optional[bool] = None
    previous_pregnancies: Optional[int] = None
    previous_deliveries: Optional[int] = None
    previous_miscarriages: Optional[int] = None
    previous_cesareans: Optional[int] = None
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

class MedicalRecordUpdate(MedicalRecordBase):
    pass

class MedicalRecordResponse(MedicalRecordBase):
    medical_record_id: int
    patient_id: int
    doctor_id: int
    current_gestational_weeks: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ConsultationSummary(BaseModel):
    consultation_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MedicalRecordSearchResult(BaseModel):
    patient_id: int
    user_id: int
    name: str
    last_name: str
    current_gestational_weeks: Optional[int] = None
    age: Optional[int] = None
    medical_record: MedicalRecordResponse

    model_config = ConfigDict(from_attributes=True)

class RiskEvaluationResponse(BaseModel):
    status: str  # ok | insufficient_data | ml_unavailable
    prediction: Optional[dict] = None
    missing_fields: Optional[List[str]] = None
    ml_model_version: Optional[str] = None
    predicted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class PatientMedicalRecordResponse(BaseModel):
    user_id: int
    name: str
    last_name: str
    current_gestational_weeks: Optional[int] = None
    age: Optional[int] = None
    medical_record: Optional[MedicalRecordResponse] = None
    consultations: List[ConsultationSummary]
    risk_prediction: Optional[dict] = None
    symptom_alert: List[AggregatedSymptomResponse] = []

    model_config = ConfigDict(from_attributes=True)
