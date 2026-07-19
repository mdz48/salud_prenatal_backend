from pydantic import BaseModel
from app.chat.domain.chat_message_entity import ChatMessage


class InboxSummary(BaseModel):
    """Lo que chat sabe por si solo: conversacion agregada, sin datos del interlocutor."""
    other_user_id: int
    last_message: ChatMessage
    unread_count: int


class ChatUser(BaseModel):
    """Lo minimo que chat necesita saber de un usuario. Contrato de chat, no de users."""
    user_id: int
    name: str
    last_name: str
    role: str
