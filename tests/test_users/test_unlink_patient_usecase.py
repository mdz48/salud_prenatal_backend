import pytest
from unittest.mock import MagicMock
from app.features.users.application.patient.unlink_patient_usecase import UnlinkPatientUseCase
from app.features.users.domain.patient_entity import PatientEntity

def test_unlink_patient_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    appointment_lookup = MagicMock()
    usecase = UnlinkPatientUseCase(repo, appointment_lookup)

    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(doctor_id=1, patient_id=999)

def test_unlink_patient_belongs_to_another_doctor():
    repo = MagicMock()
    patient = MagicMock()
    patient.doctor_id = 2  # Belongs to doctor 2
    repo.get_by_id.return_value = patient
    appointment_lookup = MagicMock()
    usecase = UnlinkPatientUseCase(repo, appointment_lookup)

    with pytest.raises(ValueError, match="Patient does not belong to this doctor"):
        usecase.execute(doctor_id=1, patient_id=5)  # Doctor 1 requests

def test_unlink_patient_success():
    repo = MagicMock()
    patient = MagicMock()
    patient.doctor_id = 1
    patient.patient_id = 5
    repo.get_by_id.return_value = patient

    updated_patient = MagicMock()
    repo.update_doctor.return_value = updated_patient

    appointment_lookup = MagicMock()
    usecase = UnlinkPatientUseCase(repo, appointment_lookup)

    result = usecase.execute(doctor_id=1, patient_id=5)

    assert result == updated_patient
    appointment_lookup.cancel_future_appointments.assert_called_once_with(5, 1)
    repo.update_doctor.assert_called_once_with(5, None)
