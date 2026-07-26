from app.patient_diaries.domain.notification import Notification


def test_notification_starts_without_errors():
    notification = Notification()

    assert notification.has_errors() is False
    assert notification.errors == []


def test_notification_accumulates_multiple_errors_without_stopping_at_first():
    notification = Notification()

    notification.add_error("El peso debe estar entre 20 y 300 kg.")
    notification.add_error("La presión sistólica debe estar entre 40 y 300 mmHg.")

    assert notification.has_errors() is True
    assert notification.errors == [
        "El peso debe estar entre 20 y 300 kg.",
        "La presión sistólica debe estar entre 40 y 300 mmHg.",
    ]


def test_notification_message_joins_all_errors():
    notification = Notification()
    notification.add_error("Error A")
    notification.add_error("Error B")

    assert notification.message() == "Error A; Error B"
