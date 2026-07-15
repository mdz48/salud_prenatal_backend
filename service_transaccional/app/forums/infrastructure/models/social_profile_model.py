from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from salud_prenatal_shared_core.database import Base

class SocialProfileModel(Base):
    __tablename__ = "social_profiles"

    user_id = Column(Integer, primary_key=True, index=True)
    alias = Column(String(50), unique=True, index=True, nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    office_address = Column(String(255), nullable=True)
    cluster_profile = Column(String(50), nullable=True)
