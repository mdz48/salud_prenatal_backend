from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    message_id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
