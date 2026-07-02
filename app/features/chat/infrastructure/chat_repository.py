from typing import List
from sqlalchemy.orm import Session
from app.features.chat.infrastructure.models.chat_model import Message
from app.features.users.infrastructure.models.user_model import Usuario
from app.features.chat.domain.entities import ChatMessage, InboxItemResponse
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

    def get_inbox(self, current_user_id: int) -> List[InboxItemResponse]:
        messages = self.db.query(Message).filter(
            (Message.sender_id == current_user_id) | (Message.receiver_id == current_user_id)
        ).order_by(Message.created_at.desc()).all()
        
        inbox_dict = {}
        for msg in messages:
            other_id = msg.receiver_id if msg.sender_id == current_user_id else msg.sender_id
            
            if other_id not in inbox_dict:
                inbox_dict[other_id] = {
                    "last_message": msg,
                    "unread_count": 0
                }
            
            if msg.receiver_id == current_user_id and not msg.is_read:
                inbox_dict[other_id]["unread_count"] += 1

        if not inbox_dict:
            return []

        other_user_ids = list(inbox_dict.keys())
        users = self.db.query(Usuario).filter(Usuario.user_id.in_(other_user_ids)).all()
        user_map = {u.user_id: u for u in users}

        result = []
        for other_id, data in inbox_dict.items():
            user = user_map.get(other_id)
            if user:
                result.append(InboxItemResponse(
                    other_user_id=user.user_id,
                    other_user_name=user.name,
                    other_user_lastname=user.last_name,
                    other_user_role=user.role.value if hasattr(user.role, 'value') else str(user.role),
                    last_message=ChatMessage.model_validate(data["last_message"]),
                    unread_count=data["unread_count"]
                ))
        
        result.sort(key=lambda x: x.last_message.created_at, reverse=True)
        return result
