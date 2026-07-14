from unittest.mock import MagicMock, patch

from app.features.notifications.application.tasks import send_daily_bitacora_reminder_job

MODULE = "app.features.notifications.application.tasks"


def _patches(tokens):
    fake_db = MagicMock()
    fake_repo = MagicMock()
    fake_repo.get_all_tokens.return_value = tokens
    # tasks.py hace db = get_session_factory()(): get_session_factory() debe
    # devolver el "sessionmaker" (callable) que a su vez devuelve fake_db.
    session_factory = MagicMock(return_value=fake_db)
    session_local = MagicMock(return_value=session_factory)
    repo_cls = MagicMock(return_value=fake_repo)
    return fake_db, fake_repo, session_local, repo_cls


class TestSendDailyBitacoraReminderJob:
    def test_does_nothing_when_no_tokens(self):
        fake_db, fake_repo, session_local, repo_cls = _patches([])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            send_daily_bitacora_reminder_job()

        fcm.send_multicast_notification.assert_not_called()
        fake_db.close.assert_called_once()

    def test_sends_notification_with_expected_title_body_and_data(self):
        fake_db, fake_repo, session_local, repo_cls = _patches(["tok-1", "tok-2"])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            send_daily_bitacora_reminder_job()

        fcm.send_multicast_notification.assert_called_once()
        tokens_arg, title_arg, body_arg, data_arg = fcm.send_multicast_notification.call_args.args
        assert tokens_arg == ["tok-1", "tok-2"]
        assert title_arg == "Recordatorio diario"
        assert "bitácora" in body_arg
        assert data_arg == {"type": "daily_reminder"}

    def test_deletes_invalid_tokens_returned_by_fcm(self):
        fake_db, fake_repo, session_local, repo_cls = _patches(["tok-1", "tok-2"])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = ["tok-2"]
            send_daily_bitacora_reminder_job()

        fake_repo.delete_token.assert_called_once_with("tok-2")

    def test_does_not_delete_anything_when_all_succeed(self):
        fake_db, fake_repo, session_local, repo_cls = _patches(["tok-1"])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            send_daily_bitacora_reminder_job()

        fake_repo.delete_token.assert_not_called()

    def test_closes_db_session_even_when_fcm_raises(self):
        fake_db, fake_repo, session_local, repo_cls = _patches(["tok-1"])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.side_effect = RuntimeError("fcm down")
            send_daily_bitacora_reminder_job()  # no debe propagar la excepción

        fake_db.close.assert_called_once()

    def test_batches_more_than_500_tokens(self):
        tokens = [f"tok-{i}" for i in range(750)]
        fake_db, fake_repo, session_local, repo_cls = _patches(tokens)
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            send_daily_bitacora_reminder_job()

        assert fcm.send_multicast_notification.call_count == 2
        first_batch = fcm.send_multicast_notification.call_args_list[0].args[0]
        second_batch = fcm.send_multicast_notification.call_args_list[1].args[0]
        assert len(first_batch) == 500
        assert len(second_batch) == 250

    def test_exactly_500_tokens_is_a_single_batch(self):
        tokens = [f"tok-{i}" for i in range(500)]
        fake_db, fake_repo, session_local, repo_cls = _patches(tokens)
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            send_daily_bitacora_reminder_job()

        assert fcm.send_multicast_notification.call_count == 1

    def test_501_tokens_creates_a_second_small_batch(self):
        tokens = [f"tok-{i}" for i in range(501)]
        fake_db, fake_repo, session_local, repo_cls = _patches(tokens)
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            send_daily_bitacora_reminder_job()

        assert fcm.send_multicast_notification.call_count == 2
        second_batch = fcm.send_multicast_notification.call_args_list[1].args[0]
        assert len(second_batch) == 1

    def test_invalid_tokens_from_multiple_batches_are_all_deleted(self):
        tokens = [f"tok-{i}" for i in range(600)]
        fake_db, fake_repo, session_local, repo_cls = _patches(tokens)
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.side_effect = [["tok-1"], ["tok-599"]]
            send_daily_bitacora_reminder_job()

        deleted = {c.args[0] for c in fake_repo.delete_token.call_args_list}
        assert deleted == {"tok-1", "tok-599"}

    def test_uses_repository_bound_to_the_session_db(self):
        fake_db, fake_repo, session_local, repo_cls = _patches([])
        with patch(f"{MODULE}.get_session_factory", session_local), \
                patch(f"{MODULE}.DeviceTokenRepository", repo_cls), \
                patch(f"{MODULE}.FirebaseNotificationService"):
            send_daily_bitacora_reminder_job()

        repo_cls.assert_called_once_with(fake_db)
