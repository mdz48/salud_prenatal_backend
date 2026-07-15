from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from salud_prenatal_shared_core.database import Base

class Consultation(Base):
    __tablename__ = "consultations"

    consultation_id = Column(Integer, primary_key=True, autoincrement=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.medical_record_id"), nullable=False, index=True)
    notes = Column(String(255), nullable=True) # Notas
    objective = Column(String(255), nullable=True) # (O)Objetivo
    plan = Column(String(255), nullable=True) # Plan, es una lista de lo que se tiene que hacer
    reported_facts = Column(String(255), nullable=False) # Datos reportados por el paciente, en el formato es la S(Subjetivo)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="consultations") 