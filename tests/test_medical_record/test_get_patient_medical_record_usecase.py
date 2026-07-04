import pytest
from unittest.mock import MagicMock
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase

def test_get_patient_medical_record_success():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    ml_service = MagicMock()
    
    usecase = GetPatientMedicalRecordUseCase(mr_repo, patient_repo, ml_service)
    
    patient_id = 1
    doctor_id = 2
    
    patient_mock = MagicMock()
    patient_mock.user_id = 1
    patient_mock.user.name = "Test"
    patient_mock.user.last_name = "User"
    patient_mock.current_gestational_weeks = 20
    patient_mock.age = 30
    patient_repo.get_by_id.return_value = patient_mock
    
    mr_mock = MagicMock()
    mr_mock.consultations = []
    mr_mock.patient_diaries = []
    mr_repo.get_by_patient_and_doctor.return_value = mr_mock
    
    ml_service.predict.return_value = {"risk": 0.5}
    
    result = usecase.execute(patient_id, doctor_id)
    
    assert result["user_id"] == 1
    assert result["name"] == "Test"
    assert result["risk_prediction"] == {"risk": 0.5}

def test_get_patient_medical_record_patient_not_found():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    ml_service = MagicMock()
    usecase = GetPatientMedicalRecordUseCase(mr_repo, patient_repo, ml_service)
    
    patient_repo.get_by_id.return_value = None
    
    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(1, 2)
