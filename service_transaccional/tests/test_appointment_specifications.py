from datetime import datetime
from unittest.mock import MagicMock

from app.appointments.domain.appointment_entity import AppointmentEntity
from app.appointments.domain.specifications import (
    DoctorAvailabilitySpecification,
    ActivePatientLinkSpecification,
)
from salud_prenatal_shared_core.enums import AppointmentStatusEnum


def _entity(doctor_id=20, patient_id=10, appointment_date=None, status=AppointmentStatusEnum.pending):
    return AppointmentEntity(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date or datetime(2026, 8, 1, 10, 0),
        status=status,
    )


def test_doctor_availability_specification_rejects_conflicting_slot():
    existing = _entity(appointment_date=datetime(2026, 8, 1, 10, 0))
    appointment_repo = MagicMock()
    appointment_repo.get_by_doctor_id.return_value = [existing]

    spec = DoctorAvailabilitySpecification(appointment_repo=appointment_repo)
    candidate = _entity(appointment_date=datetime(2026, 8, 1, 10, 0))

    assert spec.is_satisfied_by(candidate) is False


def test_doctor_availability_specification_ignores_cancelled_slot():
    existing = _entity(appointment_date=datetime(2026, 8, 1, 10, 0), status=AppointmentStatusEnum.cancelled)
    appointment_repo = MagicMock()
    appointment_repo.get_by_doctor_id.return_value = [existing]

    spec = DoctorAvailabilitySpecification(appointment_repo=appointment_repo)
    candidate = _entity(appointment_date=datetime(2026, 8, 1, 10, 0))

    assert spec.is_satisfied_by(candidate) is True


def test_doctor_availability_specification_allows_free_slot():
    appointment_repo = MagicMock()
    appointment_repo.get_by_doctor_id.return_value = []

    spec = DoctorAvailabilitySpecification(appointment_repo=appointment_repo)
    candidate = _entity()

    assert spec.is_satisfied_by(candidate) is True


def test_active_patient_link_specification_accepts_linked_patient():
    patient_lookup = MagicMock()
    patient = MagicMock(doctor_id=20)
    patient_lookup.get_by_id.return_value = patient

    spec = ActivePatientLinkSpecification(patient_lookup=patient_lookup)
    candidate = _entity(doctor_id=20, patient_id=10)

    assert spec.is_satisfied_by(candidate) is True


def test_active_patient_link_specification_rejects_unlinked_patient():
    patient_lookup = MagicMock()
    patient = MagicMock(doctor_id=99)
    patient_lookup.get_by_id.return_value = patient

    spec = ActivePatientLinkSpecification(patient_lookup=patient_lookup)
    candidate = _entity(doctor_id=20, patient_id=10)

    assert spec.is_satisfied_by(candidate) is False


def test_active_patient_link_specification_rejects_missing_patient():
    patient_lookup = MagicMock()
    patient_lookup.get_by_id.return_value = None

    spec = ActivePatientLinkSpecification(patient_lookup=patient_lookup)
    candidate = _entity(doctor_id=20, patient_id=10)

    assert spec.is_satisfied_by(candidate) is False
