"""Implementa IPatientInfoPort leyendo `patients` + `users` directo de la DB
compartida (read-models), en vez de llamar al repositorio del servicio usuarios.
El puerto (IPatientInfoPort) y el DTO (PatientInfo) no cambian: aquí brilla el
patrón hexagonal — solo cambia esta implementación.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.medical_record.domain.ports import IPatientInfoPort
from app.medical_record.domain.dtos import PatientInfo
from app.readmodels.users_readmodels import PatientRead, UserRead


class PatientInfoAdapter(IPatientInfoPort):
    def __init__(self, db: Session):
        self.db = db

    def get_patient_info(self, patient_id: int) -> Optional[PatientInfo]:
        patient = self.db.query(PatientRead).filter(PatientRead.patient_id == patient_id).first()
        return self._to_patient_info(patient)

    def get_patients_by_doctor(self, doctor_id: int) -> List[PatientInfo]:
        patients = self.db.query(PatientRead).filter(PatientRead.doctor_id == doctor_id).all()
        infos = [self._to_patient_info(p) for p in patients]
        return [info for info in infos if info]

    def _to_patient_info(self, patient):
        if not patient:
            return None
        user = self.db.query(UserRead).filter(UserRead.user_id == patient.user_id).first()
        if not user:
            return None
        return PatientInfo(
            patient_id=patient.patient_id,
            user_id=patient.user_id,
            name=user.name,
            last_name=user.last_name,
            age=patient.age,
            doctor_id=patient.doctor_id,
            birthdate=str(patient.birthdate) if patient.birthdate else None,
        )
