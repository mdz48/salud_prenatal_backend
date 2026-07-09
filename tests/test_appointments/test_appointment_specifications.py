"""ADR-08 Specification + ADR-04 Observer en la creación de citas."""
from unittest.mock import MagicMock

import pytest

from app.core.events.event_bus import EventBus
from app.core.events.events import AppointmentCreatedEvent
from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.specifications import (
    DoctorExistsSpecification,
    PatientExistsSpecification,
)
from app.features.appointments.domain.appointment_entity import AppointmentEntity


def _entity():
    return AppointmentEntity(patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")


def test_patient_exists_specification():
    lookup = MagicMock()
    lookup.get_by_id.return_value = object()
    assert PatientExistsSpecification(lookup).is_satisfied_by(_entity()) is True
    lookup.get_by_id.return_value = None
    assert PatientExistsSpecification(lookup).is_satisfied_by(_entity()) is False


def test_doctor_exists_specification():
    lookup = MagicMock()
    lookup.get_by_id.return_value = None
    assert DoctorExistsSpecification(lookup).is_satisfied_by(_entity()) is False


def test_create_appointment_publishes_event():
    repo = MagicMock()
    created = AppointmentEntity(appointment_id=99, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")
    repo.create.return_value = created
    patient_repo = MagicMock(); patient_repo.get_by_id.return_value = True
    doctor_repo = MagicMock(); doctor_repo.get_by_id.return_value = True

    received = []

    class _Handler:
        def handle(self, event):
            received.append(event)

    bus = EventBus()
    bus.subscribe(AppointmentCreatedEvent, _Handler())

    usecase = CreateAppointmentUseCase(repo, patient_repo, doctor_repo, event_bus=bus)
    result = usecase.execute(_entity())

    assert result.appointment_id == 99
    assert len(received) == 1
    assert received[0].appointment_id == 99
    assert received[0].patient_id == 1


def test_create_appointment_without_bus_still_works():
    repo = MagicMock()
    repo.create.return_value = _entity()
    patient_repo = MagicMock(); patient_repo.get_by_id.return_value = True
    doctor_repo = MagicMock(); doctor_repo.get_by_id.return_value = True

    usecase = CreateAppointmentUseCase(repo, patient_repo, doctor_repo)
    usecase.execute(_entity())
    repo.create.assert_called_once()
