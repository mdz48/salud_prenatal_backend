import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import WebSocketDisconnect

from app.features.chat.infrastructure.controllers.chat_controller import ChatController

MODULE = "app.features.chat.infrastructure.controllers.chat_controller"


class FakeManager:
    """Sustituye al singleton `manager` real para no compartir estado
    (active_connections) entre tests."""

    def __init__(self, online_user_ids=None):
        self.active_connections = {uid: MagicMock() for uid in (online_user_ids or [])}
        self.sent = []
        self.disconnected = []

    async def connect(self, websocket, user_id):
        pass

    def disconnect(self, user_id):
        self.disconnected.append(user_id)

    async def send_personal_message(self, message, user_id):
        self.sent.append((user_id, message))


class FakeWebSocket:
    def __init__(self, messages):
        self._messages = list(messages)

    async def receive_json(self):
        if not self._messages:
            raise WebSocketDisconnect()
        return self._messages.pop(0)


def _make_message(sender_id, receiver_id, content, message_id=1):
    return SimpleNamespace(
        message_id=message_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        created_at=None,
        is_read=False,
    )


def _build_controller():
    get_history = MagicMock()
    save_message = MagicMock()
    get_inbox = MagicMock()
    device_token_repository = MagicMock()
    user_repository = MagicMock()
    controller = ChatController(
        get_history, save_message, get_inbox, device_token_repository, user_repository
    )
    return controller, save_message, device_token_repository, user_repository


class TestSendChatPushNotification:
    def test_no_push_when_receiver_has_no_tokens(self):
        controller, _, device_token_repository, user_repository = _build_controller()
        device_token_repository.get_tokens_by_user_id.return_value = []

        with patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            controller._send_chat_push_notification(sender_id=1, receiver_id=2, content="hola")

        fcm.send_multicast_notification.assert_not_called()

    def test_push_uses_sender_name_as_title_and_content_as_body(self):
        controller, _, device_token_repository, user_repository = _build_controller()
        device_token_repository.get_tokens_by_user_id.return_value = ["tok-1"]
        user_repository.get_by_id.return_value = SimpleNamespace(name="Ana")

        with patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            controller._send_chat_push_notification(sender_id=1, receiver_id=2, content="Hola, ¿cómo estás?")

        tokens_arg, title_arg, body_arg, data_arg = fcm.send_multicast_notification.call_args.args
        assert tokens_arg == ["tok-1"]
        assert title_arg == "Ana"
        assert body_arg == "Hola, ¿cómo estás?"
        assert data_arg == {"type": "chat_message", "sender_id": "1"}

    def test_falls_back_to_generic_title_when_sender_not_found(self):
        controller, _, device_token_repository, user_repository = _build_controller()
        device_token_repository.get_tokens_by_user_id.return_value = ["tok-1"]
        user_repository.get_by_id.return_value = None

        with patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            controller._send_chat_push_notification(sender_id=1, receiver_id=2, content="hola")

        title_arg = fcm.send_multicast_notification.call_args.args[1]
        assert title_arg == "Nuevo mensaje"

    def test_deletes_invalid_tokens(self):
        controller, _, device_token_repository, user_repository = _build_controller()
        device_token_repository.get_tokens_by_user_id.return_value = ["tok-1", "tok-2"]
        user_repository.get_by_id.return_value = SimpleNamespace(name="Ana")

        with patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = ["tok-2"]
            controller._send_chat_push_notification(sender_id=1, receiver_id=2, content="hola")

        device_token_repository.delete_token.assert_called_once_with("tok-2")

    def test_swallows_exceptions_without_propagating(self):
        controller, _, device_token_repository, user_repository = _build_controller()
        device_token_repository.get_tokens_by_user_id.side_effect = RuntimeError("db down")

        # No debe lanzar: un fallo de push nunca debe tumbar el WebSocket.
        controller._send_chat_push_notification(sender_id=1, receiver_id=2, content="hola")


class TestWebsocketEndpointTriggersPush:
    def _run(self, controller, websocket, user_id):
        asyncio.run(controller.websocket_endpoint(websocket, user_id))

    def test_sends_push_when_receiver_is_offline(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        save_message.execute.return_value = _make_message(sender_id=1, receiver_id=2, content="hola")
        device_token_repository.get_tokens_by_user_id.return_value = ["tok-1"]
        user_repository.get_by_id.return_value = SimpleNamespace(name="Ana")

        fake_manager = FakeManager(online_user_ids=[1])  # solo el emisor está online
        ws = FakeWebSocket([{"receiver_id": 2, "content": "hola"}])

        with patch(f"{MODULE}.manager", fake_manager), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            self._run(controller, ws, user_id=1)

        fcm.send_multicast_notification.assert_called_once()

    def test_does_not_send_push_when_receiver_is_online(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        save_message.execute.return_value = _make_message(sender_id=1, receiver_id=2, content="hola")

        fake_manager = FakeManager(online_user_ids=[1, 2])  # ambos conectados
        ws = FakeWebSocket([{"receiver_id": 2, "content": "hola"}])

        with patch(f"{MODULE}.manager", fake_manager), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            self._run(controller, ws, user_id=1)

        fcm.send_multicast_notification.assert_not_called()

    def test_echoes_message_back_to_sender_regardless_of_receiver_status(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        save_message.execute.return_value = _make_message(sender_id=1, receiver_id=2, content="hola")
        device_token_repository.get_tokens_by_user_id.return_value = []

        fake_manager = FakeManager(online_user_ids=[1])
        ws = FakeWebSocket([{"receiver_id": 2, "content": "hola"}])

        with patch(f"{MODULE}.manager", fake_manager), \
                patch(f"{MODULE}.FirebaseNotificationService"):
            self._run(controller, ws, user_id=1)

        sent_to_sender = [m for uid, m in fake_manager.sent if uid == 1]
        assert len(sent_to_sender) == 1

    def test_skips_message_without_receiver_id(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        fake_manager = FakeManager()
        ws = FakeWebSocket([{"content": "hola"}])  # falta receiver_id

        with patch(f"{MODULE}.manager", fake_manager):
            self._run(controller, ws, user_id=1)

        save_message.execute.assert_not_called()

    def test_skips_message_without_content(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        fake_manager = FakeManager()
        ws = FakeWebSocket([{"receiver_id": 2}])  # falta content

        with patch(f"{MODULE}.manager", fake_manager):
            self._run(controller, ws, user_id=1)

        save_message.execute.assert_not_called()

    def test_disconnects_from_manager_on_websocket_disconnect(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        fake_manager = FakeManager()
        ws = FakeWebSocket([])  # se desconecta de inmediato

        with patch(f"{MODULE}.manager", fake_manager):
            self._run(controller, ws, user_id=1)

        assert fake_manager.disconnected == [1]

    def test_sends_one_push_per_offline_message_in_same_session(self):
        controller, save_message, device_token_repository, user_repository = _build_controller()
        save_message.execute.side_effect = [
            _make_message(sender_id=1, receiver_id=2, content="hola", message_id=1),
            _make_message(sender_id=1, receiver_id=2, content="cómo estás?", message_id=2),
        ]
        device_token_repository.get_tokens_by_user_id.return_value = ["tok-1"]
        user_repository.get_by_id.return_value = SimpleNamespace(name="Ana")

        fake_manager = FakeManager(online_user_ids=[1])
        ws = FakeWebSocket([
            {"receiver_id": 2, "content": "hola"},
            {"receiver_id": 2, "content": "cómo estás?"},
        ])

        with patch(f"{MODULE}.manager", fake_manager), \
                patch(f"{MODULE}.FirebaseNotificationService") as fcm:
            fcm.send_multicast_notification.return_value = []
            self._run(controller, ws, user_id=1)

        assert fcm.send_multicast_notification.call_count == 2

    def test_a_push_failure_does_not_break_the_websocket_loop(self):
        # Si el push explota, el resto del flujo (guardar/echo) debe seguir.
        controller, save_message, device_token_repository, user_repository = _build_controller()
        save_message.execute.return_value = _make_message(sender_id=1, receiver_id=2, content="hola")
        device_token_repository.get_tokens_by_user_id.side_effect = RuntimeError("boom")

        fake_manager = FakeManager(online_user_ids=[1])
        ws = FakeWebSocket([{"receiver_id": 2, "content": "hola"}])

        with patch(f"{MODULE}.manager", fake_manager):
            self._run(controller, ws, user_id=1)  # no debe lanzar

        assert len(fake_manager.sent) == 2  # al receptor (offline) + eco al emisor
