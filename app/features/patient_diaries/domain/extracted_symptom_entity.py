from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ExtractedSymptomEntity(BaseModel):
    """Sintoma extraido del texto libre de la bitacora por el pipeline NLP.

    `code` es el concepto clinico normalizado (MAREO, CEFALEA, FIEBRE...),
    `raw_text` el fragmento original ("me senti mareada"), `negated` indica si
    aparecia negado ("no tuve dolor"), y `alarm` marca signos de alarma obstetrica
    (varios son datos de preeclampsia)."""

    diary_symptom_id: Optional[int] = None
    patient_diary_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    code: str
    label: Optional[str] = None
    raw_text: Optional[str] = None
    negated: bool = False
    score: Optional[float] = None
    alarm: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
