from typing import List, Optional
from salud_prenatal_shared_core.text import normalize_text
from app.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort
from app.medical_record.domain.dtos import PatientInfo


class SearchMedicalRecordsByPatientNameUseCase:
    def __init__(self, medical_record_repository: IMedicalRecordRepository, patient_repository: IPatientInfoPort):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int, name: Optional[str] = None, last_name: Optional[str] = None) -> List[dict]:
        if not name and not last_name:
            raise ValueError("Debe proporcionar nombre o apellido para buscar")

        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        results = []
        for patient in patients:
            if not self._matches(patient, name, last_name):
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

    @staticmethod
    def _matches(patient: PatientInfo, name: Optional[str], last_name: Optional[str]) -> bool:
        if name and normalize_text(name) not in normalize_text(patient.name or ""):
            return False
        if last_name and normalize_text(last_name) not in normalize_text(patient.last_name or ""):
            return False
        return True
