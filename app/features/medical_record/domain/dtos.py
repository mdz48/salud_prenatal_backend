from typing import Optional
from pydantic import BaseModel


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
