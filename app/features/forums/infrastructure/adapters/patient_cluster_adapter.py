from typing import Optional

from app.features.forums.domain.ports import IPatientClusterLookup
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository
from app.features.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository
from app.features.medical_record.infrastructure.repositories.risk_prediction_repository import RiskPredictionRepository

class PatientClusterAdapter(IPatientClusterLookup):
    """Resuelve el cluster de riesgo de un usuario al crear su perfil social:
    user -> patient -> expediente -> ultima prediccion ok del ML."""

    def __init__(
        self,
        patient_repository: PatientRepository,
        medical_record_repository: MedicalRecordRepository,
        risk_prediction_repository: RiskPredictionRepository,
    ):
        self.patient_repository = patient_repository
        self.medical_record_repository = medical_record_repository
        self.risk_prediction_repository = risk_prediction_repository

    def get_cluster_by_user_id(self, user_id: int) -> Optional[str]:
        patient = self.patient_repository.get_by_user_id(user_id)
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
