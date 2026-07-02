from typing import List
from sqlalchemy.orm import Session
from app.features.chat.infrastructure.models.chat_model import Message
from app.features.chat.domain.entities import ChatMessage
from app.features.chat.domain.ports import IChatRepository

class ChatRepository(IChatRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, user1_id: int, user2_id: int) -> List[ChatMessage]:
        models = self.db.query(Message).filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.created_at.asc()).all()
        return [ChatMessage.model_validate(m) for m in models]

    def save_message(self, sender_id: int, receiver_id: int, content: str) -> ChatMessage:
        db_msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        self.db.add(db_msg)
        self.db.commit()
        self.db.refresh(db_msg)
        return ChatMessage.model_validate(db_msg)
