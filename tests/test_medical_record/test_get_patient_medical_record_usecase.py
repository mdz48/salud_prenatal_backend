import pytest
from unittest.mock import MagicMock
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase

def test_get_patient_medical_record_success():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    ml_service = MagicMock()

    usecase = GetPatientMedicalRecordUseCase(mr_repo, patient_repo, ml_service)

    patient_mock = MagicMock()
    patient_mock.user_id = 1
    patient_mock.name = "Test"
    patient_mock.last_name = "User"
    patient_mock.current_gestational_weeks = 20
    patient_mock.age = 30
    
    patient_repo.get_patient_info.return_value = patient_mock

    mr_mock = MagicMock()
    mr_mock.consultations = [MagicMock(consultation_id=1, created_at="2023-01-01")]
    mr_mock.patient_diaries = []
    mr_repo.get_by_patient_and_doctor.return_value = mr_mock

    ml_service.predict.return_value = {"risk": "low"}

    result = usecase.execute(patient_id=1, doctor_id=2)

    assert result["user_id"] == 1
    assert result["name"] == "Test"
    assert result["last_name"] == "User"
    assert result["current_gestational_weeks"] == 20
    assert result["age"] == 30
    assert result["medical_record"] == mr_mock
    assert len(result["consultations"]) == 1
    assert result["risk_prediction"] == {"risk": "low"}

    mr_repo.get_by_patient_and_doctor.assert_called_once_with(1, 2)
    ml_service.predict.assert_called_once_with(patient_mock, mr_mock, None)

def test_get_patient_medical_record_patient_not_found():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    ml_service = MagicMock()
    usecase = GetPatientMedicalRecordUseCase(mr_repo, patient_repo, ml_service)

    patient_repo.get_patient_info.return_value = None

    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(patient_id=1, doctor_id=2)
