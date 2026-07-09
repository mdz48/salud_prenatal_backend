"""ADR-05 Notification: validación de rangos de la bitácora."""
import pytest

from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.patient_diary_validator import PatientDiaryValidator
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from unittest.mock import MagicMock


def test_valid_diary_has_no_errors():
    diary = PatientDiaryEntity(medical_record_id=1, systolic=120, diastolic=80, weight_kg=70.0)
    assert PatientDiaryValidator().validate(diary).is_valid() is True


def test_accumulates_multiple_range_errors():
    diary = PatientDiaryEntity(medical_record_id=1, systolic=10, diastolic=400, weight_kg=5.0)
    notification = PatientDiaryValidator().validate(diary)
    assert notification.has_errors() is True
    assert len(notification.errors) >= 3


def test_diastolic_must_be_lower_than_systolic():
    diary = PatientDiaryEntity(medical_record_id=1, systolic=90, diastolic=120)
    notification = PatientDiaryValidator().validate(diary)
    assert any("menor que systolic" in e for e in notification.errors)


def test_create_usecase_rejects_out_of_range():
    repo = MagicMock()
    usecase = CreatePatientDiaryUseCase(repo)
    bad = PatientDiaryEntity(medical_record_id=1, systolic=500)
    with pytest.raises(ValueError, match="systolic"):
        usecase.execute(bad)
    repo.create.assert_not_called()
