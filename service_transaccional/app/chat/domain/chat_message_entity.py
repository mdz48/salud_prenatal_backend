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
