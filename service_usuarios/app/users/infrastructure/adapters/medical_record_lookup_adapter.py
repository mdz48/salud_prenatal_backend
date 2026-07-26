"""Implementa IMedicalRecordLookup leyendo la tabla `medical_records` directamente
de la DB compartida (read-model), en vez de llamar al repositorio del servicio
transaccional. El puerto no cambia; solo cambia esta implementación.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.users.domain.ports import IMedicalRecordLookup
from app.users.infrastructure.readmodels.medical_record_readmodel import MedicalRecordRead


class MedicalRecordLookupAdapter(IMedicalRecordLookup):
    def __init__(self, db: Session):
        self.db = db

    def _get(self, patient_id: int, doctor_id: int) -> Optional[MedicalRecordRead]:
        return (
            self.db.query(MedicalRecordRead)
            .filter(MedicalRecordRead.patient_id == patient_id, MedicalRecordRead.doctor_id == doctor_id)
            .first()
        )

    def get_medical_record_id(self, patient_id: int, doctor_id: int) -> Optional[int]:
        mr = self._get(patient_id, doctor_id)
        return mr.medical_record_id if mr else None

    def get_current_gestational_weeks(self, patient_id: int, doctor_id: int) -> Optional[int]:
        mr = self._get(patient_id, doctor_id)
        return mr.current_gestational_weeks if mr else None
