from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from salud_prenatal_shared_core.database import Base

class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    invitation_code_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(8), unique=True, index=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_by_patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=True)

    # Relationships
    doctor = relationship("Doctor")
    used_by_patient = relationship("Patient")
