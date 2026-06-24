from typing import Dict
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.features.chat.models.chat_model import Message

class ConnectionManager:
    def __init__(self):
        # Maps user_id to their active WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)

class ChatService:
    def get_conversation(self, db: Session, user1_id: int, user2_id: int):
        return db.query(Message).filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.created_at.asc()).all()
        
    def save_message(self, db: Session, sender_id: int, receiver_id: int, content: str):
        db_msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg

chat_service = ChatService()
manager = ConnectionManager()
