from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from salud_prenatal_shared_core.database import Base


class UnlinkRequest(Base):
    """Solicitud de la paciente para desvincularse de su doctor.

    El flujo es paciente -> doctor: la paciente crea la solicitud (status
    'pending') y el doctor la resuelve ('approved' / 'rejected'). Solo al
    aprobarse se ejecuta la desvinculacion real (doctor_id = NULL + cancelar
    citas futuras). La paciente puede cancelar su propia solicitud pendiente
    ('cancelled').
    """
    __tablename__ = "patient_unlink_requests"

    unlink_request_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships (solo dentro del servicio usuarios).
    patient = relationship("Patient")
    doctor = relationship("Doctor")
