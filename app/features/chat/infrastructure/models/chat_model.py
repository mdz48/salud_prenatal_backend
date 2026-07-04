from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.database import Base

def get_mexico_city_time():
    return datetime.now(ZoneInfo("America/Mexico_City")).replace(tzinfo=None)

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id"), index=True, nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.user_id"), index=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_mexico_city_time)
    is_read = Column(Boolean, default=False)

    sender = relationship("Usuario", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("Usuario", foreign_keys=[receiver_id], backref="received_messages")
