from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostEntity(BaseModel):
    post_id: Optional[int] = None
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str
    is_ad: bool = False
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
