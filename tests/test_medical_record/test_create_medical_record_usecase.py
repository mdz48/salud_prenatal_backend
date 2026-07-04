import pytest
from unittest.mock import MagicMock
from app.features.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.features.medical_record.domain.medical_record_entity import MedicalRecordEntity

def test_create_medical_record_success():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    
    usecase = CreateMedicalRecordUseCase(mr_repo, patient_repo)
    
    data = MedicalRecordEntity(patient_id=1, doctor_id=2, previous_pregnancies=0, previous_deliveries=0, previous_miscarriages=0, previous_cesareans=0, diabetes=False, chronic_hypertension=False, previous_preeclampsia=False, family_history_hypertension=False, family_history_heart_disease=False, chronic_kidney_disease=False, multiple_pregnancy=False, active_smoking=False)
    
    patient_mock = MagicMock()
    patient_mock.doctor_id = 2
    patient_repo.get_by_id.return_value = patient_mock
    
    mr_repo.get_by_patient_and_doctor.return_value = None
    mr_repo.create.return_value = {"id": 1}
    
    result = usecase.execute(data)
    assert result == {"id": 1}
    mr_repo.create.assert_called_once()

def test_create_medical_record_patient_not_found():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    usecase = CreateMedicalRecordUseCase(mr_repo, patient_repo)
    
    data = MedicalRecordEntity(patient_id=1, doctor_id=2, previous_pregnancies=0, previous_deliveries=0, previous_miscarriages=0, previous_cesareans=0, diabetes=False, chronic_hypertension=False, previous_preeclampsia=False, family_history_hypertension=False, family_history_heart_disease=False, chronic_kidney_disease=False, multiple_pregnancy=False, active_smoking=False)
    
    patient_repo.get_by_id.return_value = None
    
    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(data)

def test_create_medical_record_already_exists():
    mr_repo = MagicMock()
    patient_repo = MagicMock()
    usecase = CreateMedicalRecordUseCase(mr_repo, patient_repo)
    
    data = MedicalRecordEntity(patient_id=1, doctor_id=2, previous_pregnancies=0, previous_deliveries=0, previous_miscarriages=0, previous_cesareans=0, diabetes=False, chronic_hypertension=False, previous_preeclampsia=False, family_history_hypertension=False, family_history_heart_disease=False, chronic_kidney_disease=False, multiple_pregnancy=False, active_smoking=False)
    
    patient_mock = MagicMock()
    patient_mock.doctor_id = 2
    patient_repo.get_by_id.return_value = patient_mock
    
    mr_repo.get_by_patient_and_doctor.return_value = MagicMock()
    
    with pytest.raises(ValueError, match="A medical record already exists for this patient with this doctor"):
        usecase.execute(data)
