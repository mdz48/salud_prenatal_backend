from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LatestDiary(BaseModel):
    """Snapshot de la bitacora mas reciente del paciente, cruzada desde `patient_diaries`.
    Solo se traen los campos que el expediente necesita: la marca de tiempo (para el flag
    `stale`) y las mediciones que alimentan la inferencia de riesgo."""
    created_at: Optional[datetime] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    weight_kg: Optional[float] = None
    weight_gain: Optional[float] = None


class PatientInfo(BaseModel):
    """Identidad del paciente para el expediente. Lo clinico vive en el expediente,
    no aqui. Solo se cruza a `users` para nombre y edad (derivada de birthdate)."""
    patient_id: Optional[int] = None
    user_id: int
    name: str
    last_name: str
    age: Optional[int] = None
    doctor_id: Optional[int] = None
    birthdate: Optional[str] = None
