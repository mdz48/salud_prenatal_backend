from datetime import datetime
from unittest.mock import MagicMock

from app.users.application.patient.search_patient_directory_usecase import SearchPatientDirectoryUseCase
from app.users.domain.patient_directory_query import PatientDirectoryQuery


def test_without_risk_cluster_does_not_call_clinical_filter_port():
    patient_repository = MagicMock()
    clinical_filter_port = MagicMock()
    patient_repository.search_directory.return_value = ["patient1"]

    usecase = SearchPatientDirectoryUseCase(patient_repository=patient_repository, clinical_filter_port=clinical_filter_port)
    result = usecase.execute(doctor_id=1)

    clinical_filter_port.get_patient_ids_by_risk_cluster.assert_not_called()
    patient_repository.search_directory.assert_called_once_with(PatientDirectoryQuery(doctor_id=1))
    assert result == ["patient1"]


def test_with_risk_cluster_resolves_patient_ids_via_port():
    patient_repository = MagicMock()
    clinical_filter_port = MagicMock()
    clinical_filter_port.get_patient_ids_by_risk_cluster.return_value = [10, 20]
    patient_repository.search_directory.return_value = ["patient10", "patient20"]

    usecase = SearchPatientDirectoryUseCase(patient_repository=patient_repository, clinical_filter_port=clinical_filter_port)
    result = usecase.execute(doctor_id=1, risk_cluster="alto")

    clinical_filter_port.get_patient_ids_by_risk_cluster.assert_called_once_with(doctor_id=1, risk_cluster="alto")
    patient_repository.search_directory.assert_called_once_with(
        PatientDirectoryQuery(doctor_id=1, patient_ids_filter=[10, 20])
    )
    assert result == ["patient10", "patient20"]


def test_with_risk_cluster_and_no_matches_short_circuits_without_querying_repository():
    patient_repository = MagicMock()
    clinical_filter_port = MagicMock()
    clinical_filter_port.get_patient_ids_by_risk_cluster.return_value = []

    usecase = SearchPatientDirectoryUseCase(patient_repository=patient_repository, clinical_filter_port=clinical_filter_port)
    result = usecase.execute(doctor_id=1, risk_cluster="alto")

    patient_repository.search_directory.assert_not_called()
    assert result == []


def test_passes_through_linked_at_range():
    patient_repository = MagicMock()
    after = datetime(2026, 1, 1)
    before = datetime(2026, 7, 1)

    usecase = SearchPatientDirectoryUseCase(patient_repository=patient_repository)
    usecase.execute(doctor_id=3, linked_after=after, linked_before=before)

    patient_repository.search_directory.assert_called_once_with(
        PatientDirectoryQuery(doctor_id=3, linked_after=after, linked_before=before)
    )
