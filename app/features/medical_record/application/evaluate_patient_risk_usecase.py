import os

from app.features.medical_record.domain.ports import (
    ILatestDiaryPort,
    IMedicalRecordRepository,
    IMLPredictionService,
    IPatientInfoPort,
    IRiskPredictionRepository,
    ISocialClusterPort,
)
from app.features.medical_record.domain.risk_features import assess_completeness
from app.features.medical_record.domain.risk_prediction_entity import RiskPredictionEntity


class EvaluatePatientRiskUseCase:
    """Evaluacion de riesgo bajo demanda (boton del doctor).

    Cada ejecucion persiste una fila de historial: ok (prediccion del ML),
    insufficient_data (faltan datos criticos, no se llama al ML) o
    ml_unavailable (el servicio fallo). La escritura del historial nunca
    depende de que el ML este vivo.
    """

    def __init__(
        self,
        medical_record_repository: IMedicalRecordRepository,
        patient_repository: IPatientInfoPort,
        ml_prediction_service: IMLPredictionService,
        risk_prediction_repository: IRiskPredictionRepository,
        social_cluster_port: ISocialClusterPort,
        latest_diary_repository: ILatestDiaryPort,
    ):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository
        self.ml_prediction_service = ml_prediction_service
        self.risk_prediction_repository = risk_prediction_repository
        self.social_cluster_port = social_cluster_port
        self.latest_diary_repository = latest_diary_repository

    def execute(self, medical_record_id: int) -> RiskPredictionEntity:
        record = self.medical_record_repository.get_by_id(medical_record_id)
        if not record:
            raise ValueError("Medical record not found")

        patient = self.patient_repository.get_patient_info(record.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        latest_diary = self.latest_diary_repository.get_latest_diary_for_medical_record(medical_record_id)

        missing = assess_completeness(patient, record, latest_diary)
        if missing:
            return self.risk_prediction_repository.create(RiskPredictionEntity(
                medical_record_id=medical_record_id,
                status="insufficient_data",
                missing_fields=missing,
            ))

        prediction = self.ml_prediction_service.predict(patient, record, latest_diary)
        if prediction is None:
            return self.risk_prediction_repository.create(RiskPredictionEntity(
                medical_record_id=medical_record_id,
                status="ml_unavailable",
            ))

        result = self.risk_prediction_repository.create(RiskPredictionEntity(
            medical_record_id=medical_record_id,
            status="ok",
            prediction=prediction,
            ml_model_version=os.getenv("ML_MODEL_VERSION"),
        ))

        # Propagar el cluster al perfil social (si existe); nunca rompe la evaluacion.
        cluster = prediction.get("risk_cluster")
        if cluster is not None:
            try:
                self.social_cluster_port.update_cluster(patient.user_id, str(cluster))
            except Exception:
                pass

        return result
