import os
from unittest.mock import patch

from app.users.infrastructure.adapters.patient_linked_notifier_adapter import PatientLinkedNotifierAdapter


def test_notify_posts_to_transaccional_internal_endpoint():
    adapter = PatientLinkedNotifierAdapter()

    with patch.dict(
        os.environ,
        {"TRANSACCIONAL_URL": "http://transaccional:8004", "INTERNAL_SERVICE_TOKEN": "test-internal-token"},
    ), patch("app.users.infrastructure.adapters.patient_linked_notifier_adapter.requests.post") as mock_post:
        adapter.notify(patient_id=5, doctor_id=10)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://transaccional:8004/api/v1/notifications/internal/patient-linked"
    assert kwargs["json"] == {"patient_id": 5, "doctor_id": 10}
    assert kwargs["headers"] == {"X-Internal-Token": "test-internal-token"}


def test_notify_without_config_does_not_call_requests():
    adapter = PatientLinkedNotifierAdapter()

    with patch.dict(os.environ, {"TRANSACCIONAL_URL": "", "INTERNAL_SERVICE_TOKEN": ""}), \
         patch("app.users.infrastructure.adapters.patient_linked_notifier_adapter.requests.post") as mock_post:
        adapter.notify(patient_id=5, doctor_id=10)

    mock_post.assert_not_called()


def test_notify_swallows_request_exceptions():
    adapter = PatientLinkedNotifierAdapter()

    with patch.dict(
        os.environ,
        {"TRANSACCIONAL_URL": "http://transaccional:8004", "INTERNAL_SERVICE_TOKEN": "test-internal-token"},
    ), patch(
        "app.users.infrastructure.adapters.patient_linked_notifier_adapter.requests.post",
        side_effect=Exception("network down"),
    ):
        adapter.notify(patient_id=5, doctor_id=10)  # no debe propagar la excepción
