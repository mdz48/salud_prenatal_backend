from typing import List, Optional
from app.core.query.name_search_query import NameSearchCriteria
from app.features.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort


class SearchMedicalRecordsByPatientNameUseCase:
    def __init__(self, medical_record_repository: IMedicalRecordRepository, patient_repository: IPatientInfoPort):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int, name: Optional[str] = None, last_name: Optional[str] = None) -> List[dict]:
        criteria = NameSearchCriteria(name=name, last_name=last_name)
        if criteria.is_empty():
            raise ValueError("Debe proporcionar nombre o apellido para buscar")

        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        results = []
        for patient in patients:
            if not criteria.matches(patient.name, patient.last_name):
                continue
            record = self.medical_record_repository.get_by_patient_and_doctor(patient.patient_id, doctor_id)
            if not record:
                continue
            results.append({
                "patient_id": patient.patient_id,
                "user_id": patient.user_id,
                "name": patient.name,
                "last_name": patient.last_name,
                "current_gestational_weeks": record.current_gestational_weeks,
                "age": patient.age,
                "medical_record": record,
            })
        return results
