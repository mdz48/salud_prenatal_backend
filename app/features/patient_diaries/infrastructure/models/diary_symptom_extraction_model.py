from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime, Index, JSON
from sqlalchemy.sql import func


class DiarySymptomExtraction(Base):
    """Sintoma extraido por NLP de una entrada de bitacora.

    Tabla separada (no columna JSON) para que RF-31 -sintomas recurrentes- sea un
    simple GROUP BY code sobre medical_record_id. El texto crudo NO se cifra aqui
    porque ya es un derivado normalizado; el texto original vive en patient_diaries.
    `zones` guarda las zonas corporales que el NLP asocio a este sintoma especifico
    (lista pequena y de solo lectura, JSON basta; no necesita su propio GROUP BY).
    """

    __tablename__ = "diary_symptom_extractions"

    diary_symptom_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_diary_id = Column(Integer, ForeignKey("patient_diaries.patient_diary_id", ondelete="CASCADE"), nullable=False, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.medical_record_id"), nullable=True, index=True)
    code = Column(String(64), nullable=False)
    label = Column(String(128), nullable=True)
    raw_text = Column(Text, nullable=True)
    negated = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=True)
    alarm = Column(Boolean, nullable=False, default=False)
    zones = Column(JSON, nullable=True)
    model_version = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_diary_symptom_mr_code", "medical_record_id", "code"),
    )
