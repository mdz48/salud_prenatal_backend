from unittest.mock import MagicMock

import pytest

from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.patient_diaries.domain.diary_validation import PatientDiaryValidationError
from app.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase


def test_create_patient_diary_rejects_invalid_measurements_without_persisting():
    repository = MagicMock()
    usecase = CreatePatientDiaryUseCase(repository=repository)

    entity = PatientDiaryEntity(medical_record_id=1, weight_kg=1000.0, systolic=400, diastolic=1)

    with pytest.raises(PatientDiaryValidationError) as exc_info:
        usecase.execute(data=entity)

    assert len(exc_info.value.errors) == 3
    repository.create.assert_not_called()


def test_create_patient_diary_accepts_valid_measurements():
    repository = MagicMock()
    created = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1, weight_kg=70.0, systolic=120, diastolic=80)
    repository.create.return_value = created

    usecase = CreatePatientDiaryUseCase(repository=repository)
    entity = PatientDiaryEntity(medical_record_id=1, weight_kg=70.0, systolic=120, diastolic=80)

    result = usecase.execute(data=entity)

    assert result.patient_diary_id == 1
    repository.create.assert_called_once()
