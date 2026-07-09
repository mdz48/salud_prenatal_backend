from typing import Optional

from sqlalchemy.orm import Session

from app.features.medical_record.domain.ports import IRiskPredictionRepository
from app.features.medical_record.domain.risk_prediction_entity import RiskPredictionEntity
from app.features.medical_record.infrastructure.models.risk_prediction_model import RiskPrediction


class RiskPredictionRepository(IRiskPredictionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RiskPredictionEntity) -> RiskPredictionEntity:
        db_obj = RiskPrediction(**data.model_dump(exclude={"risk_prediction_id", "predicted_at"}, exclude_unset=True))
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return RiskPredictionEntity.model_validate(db_obj)

    def get_latest_for_medical_record(self, medical_record_id: int) -> Optional[RiskPredictionEntity]:
        db_obj = (
            self.db.query(RiskPrediction)
            .filter(RiskPrediction.medical_record_id == medical_record_id)
            .order_by(RiskPrediction.predicted_at.desc(), RiskPrediction.risk_prediction_id.desc())
            .first()
        )
        return RiskPredictionEntity.model_validate(db_obj) if db_obj else None

    def get_latest_ok_for_medical_record(self, medical_record_id: int) -> Optional[RiskPredictionEntity]:
        db_obj = (
            self.db.query(RiskPrediction)
            .filter(
                RiskPrediction.medical_record_id == medical_record_id,
                RiskPrediction.status == "ok",
            )
            .order_by(RiskPrediction.predicted_at.desc(), RiskPrediction.risk_prediction_id.desc())
            .first()
        )
        return RiskPredictionEntity.model_validate(db_obj) if db_obj else None
