from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class SocialProfileModel(Base):
    __tablename__ = "social_profiles"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, index=True)
    alias = Column(String(50), unique=True, index=True, nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    office_address = Column(String(255), nullable=True)
    cluster_profile = Column(String(50), nullable=True)


class CommunityGroupModel(Base):
    __tablename__ = "community_groups"

    group_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PostModel(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("community_groups.group_id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CommentModel(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True, index=True)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
