from typing import Protocol, List
from pydantic import BaseModel
from app.features.chat.domain.chat_message_entity import ChatMessage


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


class IChatRepository(Protocol):
    def get_conversation(self, user1_id: int, user2_id: int) -> List[ChatMessage]: ...
    def save_message(self, sender_id: int, receiver_id: int, content: str) -> ChatMessage: ...
    def get_inbox(self, current_user_id: int) -> List[InboxSummary]: ...


class IChatUserLookup(Protocol):
    def get_users_by_ids(self, user_ids: List[int]) -> List[ChatUser]: ...
