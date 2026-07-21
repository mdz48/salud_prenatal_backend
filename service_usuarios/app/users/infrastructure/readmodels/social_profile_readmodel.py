"""Read-model de solo lectura sobre la tabla `social_profiles` (owned por el
servicio transaccional, feature forums). `cluster_profile` es la propagación en
texto plano del risk_cluster del ML (ver EvaluatePatientRiskUseCase), usada acá
para filtrar el directorio de pacientes por nivel de riesgo (ADR-07, RF-15).
"""
from sqlalchemy import Column, Integer, String
from salud_prenatal_shared_core.database import ReadModelBase as Base


class SocialProfileRead(Base):
    __tablename__ = "social_profiles"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, primary_key=True)
    cluster_profile = Column(String(50), nullable=True)
