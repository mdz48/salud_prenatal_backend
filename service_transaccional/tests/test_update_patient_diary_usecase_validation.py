from unittest.mock import MagicMock

import pytest

from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.patient_diaries.domain.diary_validation import PatientDiaryValidationError
from app.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase


def test_update_patient_diary_rejects_invalid_measurements_without_persisting():
    repository = MagicMock()
    usecase = UpdatePatientDiaryUseCase(repository=repository)

    entity = PatientDiaryEntity(systolic=400)

    with pytest.raises(PatientDiaryValidationError):
        usecase.execute(patient_diary_id=1, data=entity)

    repository.update.assert_not_called()


def test_update_patient_diary_allows_partial_valid_measurement():
    repository = MagicMock()
    updated = PatientDiaryEntity(patient_diary_id=1, medical_record_id=1, weight_kg=71.5)
    repository.update.return_value = updated

    usecase = UpdatePatientDiaryUseCase(repository=repository)
    entity = PatientDiaryEntity(weight_kg=71.5)

    result = usecase.execute(patient_diary_id=1, data=entity)

    assert result.patient_diary_id == 1
    repository.update.assert_called_once_with(1, entity)
