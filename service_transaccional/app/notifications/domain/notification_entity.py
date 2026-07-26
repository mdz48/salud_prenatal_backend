from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationEntity(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    body: str
    type: str
    is_read: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
