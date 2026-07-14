import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.features.chat.application.get_chat_contacts_usecase import GetChatContactsUseCase
from app.features.chat.infrastructure.websocket_manager import manager
from app.features.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository
from app.features.users.infrastructure.repositories.user_repository import UserRepository
from app.core.services.firebase_service import FirebaseNotificationService

logger = logging.getLogger(__name__)

class ChatController:
    def __init__(
        self,
        get_history_usecase: GetHistoryUseCase,
        save_message_usecase: SaveMessageUseCase,
        get_chat_inbox_usecase: GetChatInboxUseCase,
        get_chat_contacts_usecase: GetChatContactsUseCase,
        device_token_repository: DeviceTokenRepository,
        user_repository: UserRepository
    ):
        self.get_history_usecase = get_history_usecase
        self.save_message_usecase = save_message_usecase
        self.get_chat_inbox_usecase = get_chat_inbox_usecase
        self.get_chat_contacts_usecase = get_chat_contacts_usecase
        self.device_token_repository = device_token_repository
        self.user_repository = user_repository

    def get_inbox(self, current_user_id: int):
        return self.get_chat_inbox_usecase.execute(current_user_id)

    def get_contacts(self, current_user_id: int, role: str):
        return self.get_chat_contacts_usecase.execute(current_user_id, role)

    def get_chat_history(self, current_user_id: int, other_user_id: int):
        return self.get_history_usecase.execute(current_user_id, other_user_id)

    async def websocket_endpoint(self, websocket: WebSocket, user_id: int):
        await manager.connect(websocket, user_id)
        try:
            while True:
                # We expect a JSON payload from the client like {"receiver_id": 2, "content": "Hello"}
                data = await websocket.receive_json()
                receiver_id = data.get("receiver_id")
                content = data.get("content")

                if receiver_id and content:
                    # Save to DB
                    db_msg = self.save_message_usecase.execute(sender_id=user_id, receiver_id=receiver_id, content=content)

                    # Format message to send back
                    msg_payload = {
                        "message_id": db_msg.message_id,
                        "sender_id": db_msg.sender_id,
                        "receiver_id": db_msg.receiver_id,
                        "content": db_msg.content,
                        "created_at": db_msg.created_at.isoformat() if db_msg.created_at else None,
                        "is_read": db_msg.is_read
                    }

                    # Send to receiver if online
                    await manager.send_personal_message(msg_payload, receiver_id)

                    # Echo back to the sender
                    await manager.send_personal_message(msg_payload, user_id)

                    # Si el receptor no tiene el WebSocket abierto (app en background
                    # o cerrada), se le manda un push para que vea el mensaje igual.
                    if receiver_id not in manager.active_connections:
                        self._send_chat_push_notification(sender_id=user_id, receiver_id=receiver_id, content=content)

        except WebSocketDisconnect:
            manager.disconnect(user_id)

    def _send_chat_push_notification(self, sender_id: int, receiver_id: int, content: str) -> None:
        try:
            tokens = self.device_token_repository.get_tokens_by_user_id(receiver_id)
            if not tokens:
                return

            sender = self.user_repository.get_by_id(sender_id)
            title = sender.name if sender else "Nuevo mensaje"
            data = {"type": "chat_message", "sender_id": str(sender_id)}

            invalid_tokens = FirebaseNotificationService.send_multicast_notification(tokens, title, content, data)
            for t in invalid_tokens:
                self.device_token_repository.delete_token(t)
        except Exception as e:
            logger.error(f"Error sending chat push notification: {e}")
