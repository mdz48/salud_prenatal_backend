from typing import List, Optional
from app.features.medical_record.domain.ports import IPatientInfoPort
from app.features.medical_record.domain.dtos import PatientInfo
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository

class PatientInfoAdapter(IPatientInfoPort):
    """
    Adapter that resolves cross-domain Patient data for MedicalRecord.
    Relies on lazy-loading `patient.user` within a live SQLAlchemy session to extract user names.
    """
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository

    def get_patient_info(self, patient_id: int) -> Optional[PatientInfo]:
        patient_entity = self.patient_repository.get_by_id(patient_id)
        if not patient_entity:
            return None
        return self._to_patient_info(patient_entity)

    def get_patients_by_doctor(self, doctor_id: int) -> List[PatientInfo]:
        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        infos = [self._to_patient_info(p) for p in patients]
        return [info for info in infos if info]

    @staticmethod
    def _to_patient_info(patient_entity) -> Optional[PatientInfo]:
        user = getattr(patient_entity, "user", None)
        if not user:
            return None

        return PatientInfo(
            patient_id=patient_entity.patient_id,
            user_id=patient_entity.user_id,
            name=user.name,
            last_name=user.last_name,
            current_gestational_weeks=patient_entity.current_gestational_weeks,
            age=patient_entity.age,
            doctor_id=patient_entity.doctor_id,
            birthdate=str(patient_entity.birthdate) if patient_entity.birthdate else None,
            residence=patient_entity.residence,
            education_level=patient_entity.education_level,
            marital_status=patient_entity.marital_status,
            height_cm=patient_entity.height_cm,
            initial_weight=patient_entity.initial_weight,
            blood_type=patient_entity.blood_type
        )
