from typing import List, Optional
from app.core.query.name_search_query import NameSearchCriteria
from app.features.users.domain.ports import IPatientRepository
from app.features.users.domain.patient_entity import PatientEntity


class SearchPatientsByNameUseCase:
    def __init__(self, patient_repository: IPatientRepository):
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int, name: Optional[str] = None, last_name: Optional[str] = None) -> List[PatientEntity]:
        criteria = NameSearchCriteria(name=name, last_name=last_name)
        if criteria.is_empty():
            raise ValueError("Debe proporcionar nombre o apellido para buscar")
        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        return [
            p for p in patients
            if p.user and criteria.matches(p.user.name, p.user.last_name)
        ]
