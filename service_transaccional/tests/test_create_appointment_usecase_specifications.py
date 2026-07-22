from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.appointments.domain.appointment_entity import AppointmentEntity
from app.appointments.application.create_appointment_usecase import CreateAppointmentUseCase


def _entity(appointment_id=None):
    return AppointmentEntity(
        appointment_id=appointment_id,
        patient_id=10,
        doctor_id=20,
        appointment_date=datetime(2026, 8, 1, 10, 0),
    )


def _base_usecase(specifications):
    appointment_repo = MagicMock()
    patient_lookup = MagicMock()
    doctor_lookup = MagicMock()
    patient_lookup.get_by_id.return_value = object()
    doctor_lookup.get_by_id.return_value = object()
    appointment_repo.create.return_value = _entity(appointment_id=1)

    return CreateAppointmentUseCase(
        appointment_repo=appointment_repo,
        patient_repo=patient_lookup,
        doctor_repo=doctor_lookup,
        specifications=specifications,
    ), appointment_repo


def test_create_appointment_raises_when_specification_violated():
    failing_spec = MagicMock()
    failing_spec.is_satisfied_by.return_value = False
    failing_spec.error_message.return_value = "El doctor ya tiene una cita agendada en la fecha y hora seleccionadas."

    usecase, appointment_repo = _base_usecase([failing_spec])

    with pytest.raises(ValueError, match="El doctor ya tiene una cita agendada"):
        usecase.execute(_entity())

    appointment_repo.create.assert_not_called()


def test_create_appointment_joins_multiple_violation_messages():
    spec_a = MagicMock()
    spec_a.is_satisfied_by.return_value = False
    spec_a.error_message.return_value = "Regla A violada."

    spec_b = MagicMock()
    spec_b.is_satisfied_by.return_value = False
    spec_b.error_message.return_value = "Regla B violada."

    usecase, _ = _base_usecase([spec_a, spec_b])

    with pytest.raises(ValueError, match="Regla A violada.; Regla B violada."):
        usecase.execute(_entity())


def test_create_appointment_succeeds_when_all_specifications_satisfied():
    passing_spec = MagicMock()
    passing_spec.is_satisfied_by.return_value = True

    usecase, appointment_repo = _base_usecase([passing_spec])

    created = usecase.execute(_entity())

    assert created.appointment_id == 1
    appointment_repo.create.assert_called_once()


def test_create_appointment_without_specifications_still_works():
    usecase, appointment_repo = _base_usecase(specifications=None)

    created = usecase.execute(_entity())

    assert created.appointment_id == 1
    appointment_repo.create.assert_called_once()
