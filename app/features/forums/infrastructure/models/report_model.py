from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True, index=True)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
