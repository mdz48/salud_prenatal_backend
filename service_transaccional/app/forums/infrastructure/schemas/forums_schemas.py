from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ProfileCreate(BaseModel):
    # user_id se deriva del token JWT, no del cliente.
    # cluster_profile tampoco se acepta del cliente: solo se deriva del ML.
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None

class ProfileUpdate(BaseModel):
    # user_id se deriva del token JWT, no del cliente.
    # cluster_profile tampoco se acepta del cliente: solo se deriva del ML.
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None

class ProfileResponse(BaseModel):
    user_id: int
    alias: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    office_address: Optional[str] = None
    # cluster_profile NO se expone: es un dato derivado de informacion medica.
    # El cluster actua server-side en /posts/recommended y /groups/recommended.

    model_config = ConfigDict(from_attributes=True)

class GroupCreate(BaseModel):
    # created_by se deriva del token JWT, no del cliente.
    name: str
    description: Optional[str] = None
    cluster_tag: Optional[str] = None

class GroupResponse(BaseModel):
    group_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_by: int
    cluster_tag: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    # author_id se deriva del token JWT, no del cliente.
    group_id: Optional[int] = None
    title: str
    content: str
    is_ad: bool = False  # solo doctores pueden marcarlo (se valida en el usecase)

class PostResponse(BaseModel):
    post_id: Optional[int] = None
    author_id: int
    group_id: Optional[int] = None
    title: str
    content: str
    is_ad: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    # author_id se deriva del token JWT, no del cliente.
    post_id: int
    content: str

class CommentResponse(BaseModel):
    comment_id: Optional[int] = None
    post_id: int
    author_id: int
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReportCreate(BaseModel):
    # reporter_id se deriva del token JWT, no del cliente.
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

class ProfileTimelineResponse(BaseModel):
    profile: ProfileResponse
    posts: List[PostResponse]

    model_config = ConfigDict(from_attributes=True)
