from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CommunityGroupEntity(BaseModel):
    group_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
