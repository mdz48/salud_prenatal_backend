"""Patrón Protection Proxy (ADR-03).

Proxy que controla el acceso a los expedientes clínicos: implementa la misma
interfaz que el repositorio real (`IMedicalRecordRepository`) pero verifica la
relación paciente-doctor antes de delegar la lectura autorizada. El resto de
operaciones se delegan sin cambios.
"""
from __future__ import annotations

from typing import Optional

from app.features.medical_record.domain.medical_record_entity import MedicalRecordEntity
from app.features.medical_record.domain.ports import (
    IMedicalRecordRepository,
    IPatientInfoPort,
)


class ProtectedMedicalRecordRepository(IMedicalRecordRepository):
    def __init__(self, real_repository: IMedicalRecordRepository, patient_info_port: IPatientInfoPort):
        self._real = real_repository
        self._patients = patient_info_port

    def get_by_patient_and_doctor(self, patient_id: int, doctor_id: int) -> Optional[MedicalRecordEntity]:
        patient = self._patients.get_patient_info(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        if patient.doctor_id != doctor_id:
            raise ValueError("El paciente no tiene una relación con este doctor")
        return self._real.get_by_patient_and_doctor(patient_id, doctor_id)

    # --- Operaciones sin restricción: se delegan tal cual ---
    def get_by_patient_id(self, patient_id: int) -> Optional[MedicalRecordEntity]:
        return self._real.get_by_patient_id(patient_id)

    def get_by_id(self, medical_record_id: int) -> Optional[MedicalRecordEntity]:
        return self._real.get_by_id(medical_record_id)

    def create(self, data: MedicalRecordEntity) -> MedicalRecordEntity:
        return self._real.create(data)

    def update(self, medical_record_id: int, data: dict) -> Optional[MedicalRecordEntity]:
        return self._real.update(medical_record_id, data)
