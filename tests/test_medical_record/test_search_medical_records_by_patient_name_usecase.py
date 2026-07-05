import pytest
from unittest.mock import MagicMock
from app.features.medical_record.application.search_medical_records_by_patient_name_usecase import (
    SearchMedicalRecordsByPatientNameUseCase,
)


def make_patient_info(patient_id, name, last_name):
    info = MagicMock()
    info.patient_id = patient_id
    info.user_id = patient_id + 100
    info.name = name
    info.last_name = last_name
    info.current_gestational_weeks = 20
    info.age = 30
    return info


def test_search_returns_records_for_matching_patients():
    mr_repo = MagicMock()
    patient_port = MagicMock()
    patient_port.get_patients_by_doctor.return_value = [
        make_patient_info(1, "María", "López"),
        make_patient_info(2, "Ana", "Ruiz"),
    ]
    record = MagicMock()
    mr_repo.get_by_patient_and_doctor.side_effect = (
        lambda patient_id, doctor_id: record if patient_id == 1 else None
    )
    usecase = SearchMedicalRecordsByPatientNameUseCase(mr_repo, patient_port)

    result = usecase.execute(doctor_id=5, name="maria")

    assert len(result) == 1
    assert result[0]["patient_id"] == 1
    assert result[0]["name"] == "María"
    assert result[0]["medical_record"] is record
    mr_repo.get_by_patient_and_doctor.assert_called_once_with(1, 5)
    patient_port.get_patients_by_doctor.assert_called_once_with(5)


def test_search_excludes_matches_without_record():
    mr_repo = MagicMock()
    patient_port = MagicMock()
    patient_port.get_patients_by_doctor.return_value = [
        make_patient_info(1, "María", "López"),
    ]
    mr_repo.get_by_patient_and_doctor.return_value = None
    usecase = SearchMedicalRecordsByPatientNameUseCase(mr_repo, patient_port)

    assert usecase.execute(doctor_id=5, last_name="lopez") == []


def test_search_without_criteria_raises():
    usecase = SearchMedicalRecordsByPatientNameUseCase(MagicMock(), MagicMock())

    with pytest.raises(ValueError):
        usecase.execute(doctor_id=5)
