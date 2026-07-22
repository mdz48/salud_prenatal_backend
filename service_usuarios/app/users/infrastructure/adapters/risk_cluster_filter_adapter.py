"""Implementa IPatientClinicalFilterPort leyendo `social_profiles.cluster_profile`
(texto plano, propagado desde el risk_cluster del ML en cada evaluación — ver
EvaluatePatientRiskUseCase) en vez del JSON `risk_predictions.prediction`: es la
única fuente de nivel de riesgo que hoy es realmente filtrable por SQL (ADR-07).

Caveat: un paciente sin perfil social (nunca entró al foro) no tiene fila en
`social_profiles` y por tanto nunca aparece en este filtro, aunque sí tenga
una predicción de riesgo vigente en `risk_predictions`.
"""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.domain.ports import IPatientClinicalFilterPort
from app.users.infrastructure.models.patient_model import Patient
from app.users.infrastructure.readmodels.social_profile_readmodel import SocialProfileRead


class RiskClusterFilterAdapter(IPatientClinicalFilterPort):
    def __init__(self, db: Session):
        self.db = db

    def get_patient_ids_by_risk_cluster(self, doctor_id: int, risk_cluster: str) -> List[int]:
        matching_user_ids = select(SocialProfileRead.user_id).where(
            SocialProfileRead.cluster_profile == risk_cluster
        )

        patient_ids = (
            self.db.query(Patient.patient_id)
            .filter(Patient.doctor_id == doctor_id, Patient.user_id.in_(matching_user_ids))
            .all()
        )
        return [pid for (pid,) in patient_ids]
