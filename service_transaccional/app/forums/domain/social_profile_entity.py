from pydantic import BaseModel, ConfigDict
from typing import Optional

class SocialProfileEntity(BaseModel):
    user_id: int
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None
    cluster_profile: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
