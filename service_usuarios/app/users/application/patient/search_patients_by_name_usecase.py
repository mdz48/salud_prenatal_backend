from typing import List, Optional
from salud_prenatal_shared_core.text import normalize_text
from app.users.domain.ports import IPatientRepository
from app.users.domain.patient_entity import PatientEntity


class SearchPatientsByNameUseCase:
    def __init__(self, patient_repository: IPatientRepository):
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int, name: Optional[str] = None, last_name: Optional[str] = None) -> List[PatientEntity]:
        if not name and not last_name:
            raise ValueError("Debe proporcionar nombre o apellido para buscar")
        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        return [p for p in patients if self._matches(p, name, last_name)]

    @staticmethod
    def _matches(patient: PatientEntity, name: Optional[str], last_name: Optional[str]) -> bool:
        user = patient.user
        if not user:
            return False
        if name and normalize_text(name) not in normalize_text(user.name or ""):
            return False
        if last_name and normalize_text(last_name) not in normalize_text(user.last_name or ""):
            return False
        return True
