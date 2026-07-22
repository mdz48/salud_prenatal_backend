from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from app.users.application.invitation.redeem_invitation_code_usecase import RedeemInvitationCodeUseCase


def test_redeem_invitation_code_notifies_patient_linked():
    patient_repo = MagicMock()
    invitation_repo = MagicMock()
    notifier = MagicMock()

    code_obj = MagicMock()
    code_obj.invitation_code_id = 1
    code_obj.doctor_id = 10
    code_obj.is_used = False
    code_obj.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    invitation_repo.get_by_code.return_value = code_obj

    patient_mock = MagicMock()
    patient_repo.update_doctor.return_value = patient_mock

    usecase = RedeemInvitationCodeUseCase(
        patient_repository=patient_repo,
        invitation_code_repository=invitation_repo,
        patient_linked_notifier=notifier,
    )

    result = usecase.execute(patient_id=5, code="ABC12345")

    assert result == patient_mock
    notifier.notify.assert_called_once_with(patient_id=5, doctor_id=10)


def test_redeem_invitation_code_without_notifier_does_not_raise():
    patient_repo = MagicMock()
    invitation_repo = MagicMock()

    code_obj = MagicMock()
    code_obj.invitation_code_id = 1
    code_obj.doctor_id = 10
    code_obj.is_used = False
    code_obj.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    invitation_repo.get_by_code.return_value = code_obj

    patient_mock = MagicMock()
    patient_repo.update_doctor.return_value = patient_mock

    usecase = RedeemInvitationCodeUseCase(
        patient_repository=patient_repo,
        invitation_code_repository=invitation_repo,
    )

    result = usecase.execute(patient_id=5, code="ABC12345")

    assert result == patient_mock
