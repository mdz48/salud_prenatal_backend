from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CommentEntity(BaseModel):
    comment_id: Optional[int] = None
    post_id: int
    author_id: int
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
