from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.patient_diaries.domain.diary_validation import PatientDiaryValidationError
from app.patient_diaries.infrastructure.controllers.patient_diary_controller import PatientDiaryController
from app.patient_diaries.infrastructure.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate


def _controller(create_use_case=None, update_use_case=None):
    return PatientDiaryController(
        create_patient_diary_use_case=create_use_case or MagicMock(),
        get_all_patient_diaries_use_case=MagicMock(),
        get_diaries_by_medical_record_use_case=MagicMock(),
        get_patient_diary_by_id_use_case=MagicMock(),
        update_patient_diary_use_case=update_use_case or MagicMock(),
        delete_patient_diary_use_case=MagicMock(),
        get_diary_symptoms_use_case=MagicMock(),
        get_medical_record_symptom_history_use_case=MagicMock(),
    )


def test_create_patient_diary_maps_validation_error_to_422():
    create_use_case = MagicMock()
    create_use_case.execute.side_effect = PatientDiaryValidationError(["El peso debe estar entre 20 y 300 kg."])
    controller = _controller(create_use_case=create_use_case)

    data = PatientDiaryCreate(medical_record_id=1, weight_kg=1000.0)

    with pytest.raises(HTTPException) as exc_info:
        controller.create_patient_diary(data=data)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == ["El peso debe estar entre 20 y 300 kg."]


def test_update_patient_diary_maps_validation_error_to_422():
    update_use_case = MagicMock()
    update_use_case.execute.side_effect = PatientDiaryValidationError(["La presión sistólica debe ser mayor que la diastólica."])
    controller = _controller(update_use_case=update_use_case)

    data = PatientDiaryUpdate(systolic=80, diastolic=90)

    with pytest.raises(HTTPException) as exc_info:
        controller.update_patient_diary(patient_diary_id=1, data=data)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == ["La presión sistólica debe ser mayor que la diastólica."]


def test_update_patient_diary_still_maps_not_found_to_404():
    update_use_case = MagicMock()
    update_use_case.execute.side_effect = ValueError("Patient diary not found")
    controller = _controller(update_use_case=update_use_case)

    data = PatientDiaryUpdate(weight_kg=70.0)

    with pytest.raises(HTTPException) as exc_info:
        controller.update_patient_diary(patient_diary_id=1, data=data)

    assert exc_info.value.status_code == 404
