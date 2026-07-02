from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class SocialProfileEntity(BaseModel):
    user_id: int
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None
    cluster_profile: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CommunityGroupEntity(BaseModel):
    group_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PostEntity(BaseModel):
    post_id: Optional[int] = None
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CommentEntity(BaseModel):
    comment_id: Optional[int] = None
    post_id: int
    author_id: int
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReportEntity(BaseModel):
    report_id: Optional[int] = None
    reporter_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
