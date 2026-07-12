import pytest
from unittest.mock import MagicMock
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.features.patient_diaries.domain.symptom_extraction_result_entity import SymptomExtractionResult

def test_create_patient_diary_usecase():
    repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo)
    data = PatientDiaryEntity(medical_record_id=1, weight_kg=70.0, weight_gain=1.0, systolic=120, diastolic=80, notes="All good")
    
    repo.create.return_value = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1)
    result = usecase.execute(data)
    
    repo.create.assert_called_once()
    assert result.patient_diary_id == 1

def test_create_patient_diary_triggers_symptom_extraction():
    repo = MagicMock()
    nlp_port = MagicMock()
    symptom_repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo, symptom_extraction_port=nlp_port, symptom_repository=symptom_repo)

    created = PatientDiaryEntity(patient_diary_id=5, medical_record_id=1, symptoms="me senti mareada y con temperatura")
    repo.create.return_value = created
    nlp_port.extract.return_value = SymptomExtractionResult(symptoms=[ExtractedSymptomEntity(code="MAREO", raw_text="mareada")])

    result = usecase.execute(created)

    assert result.patient_diary_id == 5
    nlp_port.extract.assert_called_once()
    symptom_repo.replace_for_diary.assert_called_once()
    args = symptom_repo.replace_for_diary.call_args.args
    assert args[0] == 5 and args[1] == 1  # (patient_diary_id, medical_record_id)


def test_create_patient_diary_persiste_solo_body_zones_sin_sintomas():
    from app.features.patient_diaries.domain.body_zone_entity import BodyZoneEntity

    repo = MagicMock()
    nlp_port = MagicMock()
    symptom_repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo, symptom_extraction_port=nlp_port, symptom_repository=symptom_repo)

    created = PatientDiaryEntity(patient_diary_id=7, medical_record_id=1, symptoms="hinchados los pies")
    repo.create.return_value = created
    nlp_port.extract.return_value = SymptomExtractionResult(body_zones=[BodyZoneEntity(code="PIES", raw_text="pies")])

    usecase.execute(created)

    symptom_repo.replace_for_diary.assert_called_once()


def test_create_patient_diary_survives_nlp_failure():
    repo = MagicMock()
    nlp_port = MagicMock()
    symptom_repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo, symptom_extraction_port=nlp_port, symptom_repository=symptom_repo)

    created = PatientDiaryEntity(patient_diary_id=6, medical_record_id=1, symptoms="me duele la cabeza")
    repo.create.return_value = created
    nlp_port.extract.side_effect = RuntimeError("NLP caido")

    # El fallo del NLP no debe propagarse: la bitacora se creo igual.
    result = usecase.execute(created)
    assert result.patient_diary_id == 6
    symptom_repo.replace_for_diary.assert_not_called()


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


def test_get_medical_record_symptom_history_agrega_todo():
    from datetime import datetime
    from app.features.patient_diaries.application.get_medical_record_symptom_history_usecase import (
        GetMedicalRecordSymptomHistoryUseCase,
    )
    from app.features.patient_diaries.domain.body_zone_entity import BodyZoneEntity

    repo = MagicMock()
    repo.get_by_medical_record_id.return_value = [
        ExtractedSymptomEntity(code="SANGRADO", alarm=True, created_at=datetime(2026, 6, 20, 8, 0)),
        ExtractedSymptomEntity(code="SANGRADO", created_at=datetime(2026, 6, 22, 8, 0)),
    ]
    usecase = GetMedicalRecordSymptomHistoryUseCase(repo)

    result = usecase.execute(medical_record_id=10)

    repo.get_by_medical_record_id.assert_called_once_with(10)
    assert len(result) == 1
    assert result[0].code == "SANGRADO"
    assert result[0].occurrences == 2
    assert result[0].alarm is True
