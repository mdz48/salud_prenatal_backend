from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RiskPredictionEntity(BaseModel):
    """Una evaluacion de riesgo persistida (acto clinico del doctor).

    status: "ok" (prediccion del ML), "insufficient_data" (faltan datos criticos,
    no se llamo al ML) o "ml_unavailable" (el servicio ML fallo o no esta configurado).
    """
    risk_prediction_id: Optional[int] = None
    medical_record_id: int
    status: str
    prediction: Optional[dict] = None
    missing_fields: Optional[List[str]] = None
    ml_model_version: Optional[str] = None
    predicted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
