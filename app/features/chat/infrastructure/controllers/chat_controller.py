from fastapi import WebSocket, WebSocketDisconnect

from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.features.chat.infrastructure.websocket_manager import manager

class ChatController:
    def __init__(
        self,
        get_history_usecase: GetHistoryUseCase,
        save_message_usecase: SaveMessageUseCase,
        get_chat_inbox_usecase: GetChatInboxUseCase
    ):
        self.get_history_usecase = get_history_usecase
        self.save_message_usecase = save_message_usecase
        self.get_chat_inbox_usecase = get_chat_inbox_usecase

    def get_inbox(self, current_user_id: int):
        return self.get_chat_inbox_usecase.execute(current_user_id)

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
                    
        except WebSocketDisconnect:
            manager.disconnect(user_id)
