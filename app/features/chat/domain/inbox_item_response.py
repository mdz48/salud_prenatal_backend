from pydantic import BaseModel, ConfigDict
from .chat_message_entity import ChatMessage

class InboxItemResponse(BaseModel):
    other_user_id: int
    other_user_name: str
    other_user_lastname: str
    other_user_role: str
    last_message: ChatMessage
    unread_count: int

    model_config = ConfigDict(from_attributes=True)
