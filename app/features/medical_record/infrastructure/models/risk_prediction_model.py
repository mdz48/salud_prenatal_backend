from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    risk_prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.medical_record_id"), nullable=False, index=True)
    status = Column(String(30), nullable=False)  # ok | insufficient_data | ml_unavailable
    prediction = Column(JSON, nullable=True)  # respuesta cruda del ML cuando status == ok
    missing_fields = Column(JSON, nullable=True)  # lista de campos faltantes cuando insufficient_data
    ml_model_version = Column(String(50), nullable=True)
    predicted_at = Column(DateTime, server_default=func.now(), index=True)

    medical_record = relationship("MedicalRecord")
