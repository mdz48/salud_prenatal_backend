from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ChatMessage(BaseModel):
    message_id: Optional[int] = None
    sender_id: int
    receiver_id: int
    content: str
    created_at: Optional[datetime] = None
    is_read: bool = False

    model_config = ConfigDict(from_attributes=True)

class InboxItemResponse(BaseModel):
    other_user_id: int
    other_user_name: str
    other_user_lastname: str
    other_user_role: str
    last_message: ChatMessage
    unread_count: int

    model_config = ConfigDict(from_attributes=True)
