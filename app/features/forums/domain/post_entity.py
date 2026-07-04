from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostEntity(BaseModel):
    post_id: Optional[int] = None
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
