"""IPatientClusterLookup: user -> patient -> expediente -> última predicción ok del ML.

El primer salto (user->patient) cruza a `users`: se resuelve por read-model sobre
la DB compartida. Los dos siguientes (expediente, predicción) son IN-PROCESO:
medical_record y risk_prediction son features del propio servicio transaccional,
así que se siguen usando sus repositorios directamente.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.forums.domain.ports import IPatientClusterLookup
from app.readmodels.users_readmodels import PatientRead
from app.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository
from app.medical_record.infrastructure.repositories.risk_prediction_repository import RiskPredictionRepository


class PatientClusterAdapter(IPatientClusterLookup):
    def __init__(
        self,
        db: Session,
        medical_record_repository: MedicalRecordRepository,
        risk_prediction_repository: RiskPredictionRepository,
    ):
        self.db = db
        self.medical_record_repository = medical_record_repository
        self.risk_prediction_repository = risk_prediction_repository

    def get_cluster_by_user_id(self, user_id: int) -> Optional[str]:
        patient = self.db.query(PatientRead).filter(PatientRead.user_id == user_id).first()
        if not patient:
            return None

        record = self.medical_record_repository.get_by_patient_id(patient.patient_id)
        if not record:
            return None

        latest_ok = self.risk_prediction_repository.get_latest_ok_for_medical_record(record.medical_record_id)
        if not latest_ok or not latest_ok.prediction:
            return None

        cluster = latest_ok.prediction.get("risk_cluster")
        return str(cluster) if cluster is not None else None
