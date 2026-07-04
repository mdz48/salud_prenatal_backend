from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProfileCreate(BaseModel):
    user_id: int
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None
    cluster_profile: Optional[str] = None

class ProfileResponse(BaseModel):
    user_id: int
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None
    cluster_profile: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: int

class GroupResponse(BaseModel):
    group_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str

class PostResponse(BaseModel):
    post_id: Optional[int] = None
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    post_id: int
    author_id: int
    content: str

class CommentResponse(BaseModel):
    comment_id: Optional[int] = None
    post_id: int
    author_id: int
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReportCreate(BaseModel):
    reporter_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str

class ReportResponse(BaseModel):
    report_id: Optional[int] = None
    reporter_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
