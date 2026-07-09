"""ADR-03 Protection Proxy: control de acceso a expedientes."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.features.medical_record.application.protected_medical_record_repository import (
    ProtectedMedicalRecordRepository,
)


def _proxy(patient=SimpleNamespace(doctor_id=2), record="RECORD"):
    real = MagicMock()
    real.get_by_patient_and_doctor.return_value = record
    patients = MagicMock()
    patients.get_patient_info.return_value = patient
    return ProtectedMedicalRecordRepository(real, patients), real


def test_authorized_access_delegates_to_real_repo():
    proxy, real = _proxy()
    assert proxy.get_by_patient_and_doctor(1, 2) == "RECORD"
    real.get_by_patient_and_doctor.assert_called_once_with(1, 2)


def test_patient_not_found_is_blocked():
    proxy, real = _proxy(patient=None)
    with pytest.raises(ValueError, match="Patient not found"):
        proxy.get_by_patient_and_doctor(1, 2)
    real.get_by_patient_and_doctor.assert_not_called()


def test_wrong_doctor_is_blocked():
    proxy, real = _proxy(patient=SimpleNamespace(doctor_id=99))
    with pytest.raises(ValueError, match="no tiene una relaci"):
        proxy.get_by_patient_and_doctor(1, 2)
    real.get_by_patient_and_doctor.assert_not_called()


def test_unrestricted_methods_are_delegated():
    proxy, real = _proxy()
    proxy.get_by_id(5)
    proxy.get_by_patient_id(9)
    real.get_by_id.assert_called_once_with(5)
    real.get_by_patient_id.assert_called_once_with(9)
