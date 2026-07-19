from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from salud_prenatal_shared_core.database import Base

class Receptionist(Base):
    __tablename__ = "receptionists"

    receptionist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False, index=True)

    user = relationship("Usuario", back_populates="receptionist_profile", foreign_keys=[user_id])
    doctor = relationship("Doctor", foreign_keys=[doctor_id])
