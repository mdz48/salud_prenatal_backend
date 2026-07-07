import pytest
from unittest.mock import MagicMock
from app.features.users.application.patient.search_patients_by_name_usecase import SearchPatientsByNameUseCase


def make_patient(name, last_name):
    patient = MagicMock()
    patient.user.name = name
    patient.user.last_name = last_name
    return patient


def test_search_matches_partial_ignoring_case_and_accents():
    repo = MagicMock()
    repo.get_patients_by_doctor.return_value = [
        make_patient("María", "López"),
        make_patient("Ana", "Martínez"),
    ]
    usecase = SearchPatientsByNameUseCase(repo)

    result = usecase.execute(doctor_id=1, name="mari")

    assert len(result) == 1
    assert result[0].user.name == "María"
    repo.get_patients_by_doctor.assert_called_once_with(1)


def test_search_with_name_and_last_name_requires_both_to_match():
    repo = MagicMock()
    repo.get_patients_by_doctor.return_value = [
        make_patient("María", "López"),
        make_patient("María", "Pérez"),
    ]
    usecase = SearchPatientsByNameUseCase(repo)

    result = usecase.execute(doctor_id=1, name="maria", last_name="perez")

    assert len(result) == 1
    assert result[0].user.last_name == "Pérez"


def test_search_by_last_name_only():
    repo = MagicMock()
    repo.get_patients_by_doctor.return_value = [
        make_patient("María", "López"),
        make_patient("Ana", "Martínez"),
    ]
    usecase = SearchPatientsByNameUseCase(repo)

    result = usecase.execute(doctor_id=1, last_name="martinez")

    assert len(result) == 1
    assert result[0].user.name == "Ana"


def test_search_without_criteria_raises():
    usecase = SearchPatientsByNameUseCase(MagicMock())

    with pytest.raises(ValueError):
        usecase.execute(doctor_id=1)


def test_search_skips_patients_without_user():
    patient_without_user = MagicMock()
    patient_without_user.user = None
    repo = MagicMock()
    repo.get_patients_by_doctor.return_value = [patient_without_user]
    usecase = SearchPatientsByNameUseCase(repo)

    assert usecase.execute(doctor_id=1, name="maria") == []
