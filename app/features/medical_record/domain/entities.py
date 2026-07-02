from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ConsultationEntity(BaseModel):
    consultation_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PatientDiaryEntity(BaseModel):
    patient_diary_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, extra="allow")

class MedicalRecordEntity(BaseModel):
    medical_record_id: Optional[int] = None
    patient_id: int
    doctor_id: int
    
    # Medical history
    previous_hypertension: Optional[bool] = None
    diabetes: Optional[bool] = None
    family_history_hypertension: Optional[bool] = None

    # Obstetric history
    previous_pregnancies: Optional[int] = None
    previous_deliveries: Optional[int] = None
    previous_miscarriages: Optional[int] = None
    previous_cesareans: Optional[int] = None
    previous_preeclampsia: Optional[bool] = None

    # Chronic / pathological history
    chronic_kidney_disease: Optional[bool] = None
    chronic_hypertension: Optional[bool] = None
    multiple_pregnancy: Optional[bool] = None
    fetal_death: Optional[bool] = None
    fetal_growth_restriction: Optional[bool] = None

    # Family history
    family_history_heart_disease: Optional[bool] = None

    # Lifestyle
    active_smoking: Optional[bool] = None

    consultations: Optional[List[ConsultationEntity]] = []
    patient_diaries: Optional[List[PatientDiaryEntity]] = []

    model_config = ConfigDict(from_attributes=True)
