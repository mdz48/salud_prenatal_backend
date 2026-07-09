"""Especificaciones de negocio para la creación de citas (ADR-08)."""
from __future__ import annotations

from app.core.specification import Specification
from app.features.appointments.domain.appointment_entity import AppointmentEntity
from app.features.appointments.domain.ports import IDoctorLookup, IPatientLookup


class PatientExistsSpecification(Specification[AppointmentEntity]):
    def __init__(self, patient_lookup: IPatientLookup):
        self._patient_lookup = patient_lookup

    def is_satisfied_by(self, candidate: AppointmentEntity) -> bool:
        return self._patient_lookup.get_by_id(candidate.patient_id) is not None


class DoctorExistsSpecification(Specification[AppointmentEntity]):
    def __init__(self, doctor_lookup: IDoctorLookup):
        self._doctor_lookup = doctor_lookup

    def is_satisfied_by(self, candidate: AppointmentEntity) -> bool:
        return self._doctor_lookup.get_by_id(candidate.doctor_id) is not None
