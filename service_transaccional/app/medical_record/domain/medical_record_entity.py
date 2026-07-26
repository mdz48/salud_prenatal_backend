from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from salud_prenatal_shared_core.enums import BloodTypeEnum
from salud_prenatal_shared_core.pregnancy_calculations import gestational_weeks
from .consultation_entity import ConsultationEntity
from .patient_diary_entity import PatientDiaryEntity

class MedicalRecordEntity(BaseModel):
    medical_record_id: Optional[int] = None
    patient_id: int
    doctor_id: int

    # Clinical profile (del expediente, capturado por el doctor)
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

    # Plan general del expediente (distinto del plan por consulta)
    general_plan: Optional[str] = None

    consultations: Optional[List[ConsultationEntity]] = []
    patient_diaries: Optional[List[PatientDiaryEntity]] = []

    @property
    def current_gestational_weeks(self) -> int | None:
        return gestational_weeks(self.last_menstrual_period, self.weeks_at_registration)

    model_config = ConfigDict(from_attributes=True)
