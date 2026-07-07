from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class CommunityGroupModel(Base):
    __tablename__ = "community_groups"

    group_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    cluster_tag = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
