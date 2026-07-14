from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime, Index
from sqlalchemy.sql import func


class DiaryBodyZone(Base):
    """Zona corporal detectada en el texto libre de una bitacora sin sintoma asociado
    (campo top-level `body_zones` de POST /nlp/extract-symptoms, ver
    docs/integration/nlp-integration.md §1.1). Tabla separada de
    diary_symptom_extractions porque estas zonas no cuelgan de ningun sintoma."""

    __tablename__ = "diary_body_zones"

    zone_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_diary_id = Column(Integer, ForeignKey("patient_diaries.patient_diary_id", ondelete="CASCADE"), nullable=False, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.medical_record_id"), nullable=True, index=True)
    code = Column(String(64), nullable=False)
    label = Column(String(128), nullable=True)
    raw_text = Column(Text, nullable=True)
    negated = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=True)
    model_version = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_diary_body_zone_mr_code", "medical_record_id", "code"),
    )
