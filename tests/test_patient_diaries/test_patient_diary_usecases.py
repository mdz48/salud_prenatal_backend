import pytest
from unittest.mock import MagicMock
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

def test_create_patient_diary_usecase():
    repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo)
    data = PatientDiaryEntity(medical_record_id=1, weight_kg=70.0, weight_gain=1.0, systolic=120, diastolic=80, notes="All good")
    
    repo.create.return_value = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1)
    result = usecase.execute(data)
    
    repo.create.assert_called_once()
    assert result.patient_diary_id == 1

def test_get_all_patient_diaries_usecase():
    repo = MagicMock()
    usecase = GetAllPatientDiariesUseCase(repo)
    
    repo.get_all.return_value = [PatientDiaryEntity(patient_diary_id=1, medical_record_id=1), PatientDiaryEntity(patient_diary_id=2, medical_record_id=1)]
    result = usecase.execute(0, 10)
    
    repo.get_all.assert_called_once_with(skip=0, limit=10)
    assert len(result) == 2

def test_get_patient_diary_by_id_usecase():
    repo = MagicMock()
    usecase = GetPatientDiaryByIdUseCase(repo)
    
    repo.get_by_id.return_value = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1)
    result = usecase.execute(1)
    assert result.patient_diary_id == 1
    
    repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Patient diary not found"):
        usecase.execute(2)

def test_get_diaries_by_medical_record_usecase():
    repo = MagicMock()
    usecase = GetDiariesByMedicalRecordUseCase(repo)
    
    repo.get_by_medical_record_id.return_value = [PatientDiaryEntity(patient_diary_id=1, medical_record_id=1)]
    result = usecase.execute(1)
    
    repo.get_by_medical_record_id.assert_called_once_with(1)
    assert len(result) == 1
    assert result[0].medical_record_id == 1

def test_update_patient_diary_usecase():
    repo = MagicMock()
    usecase = UpdatePatientDiaryUseCase(repo)
    
    data = PatientDiaryEntity(weight_kg=71.0)
    
    repo.update.return_value = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1, weight_kg=71.0)
    result = usecase.execute(1, data)
    assert result.weight_kg == 71.0
    
    repo.update.return_value = None
    with pytest.raises(ValueError, match="Patient diary not found"):
        usecase.execute(2, data)

def test_delete_patient_diary_usecase():
    repo = MagicMock()
    usecase = DeletePatientDiaryUseCase(repo)
    
    repo.delete.return_value = True
    result = usecase.execute(1)
    assert result is True
    
    repo.delete.return_value = False
    with pytest.raises(ValueError, match="Patient diary not found"):
        usecase.execute(2)
