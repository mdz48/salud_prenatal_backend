from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime

from .body_zone_entity import BodyZoneEntity


class ExtractedSymptomEntity(BaseModel):
    """Sintoma extraido del texto libre de la bitacora por el pipeline NLP.

    `code` es el concepto clinico normalizado (MAREO, CEFALEA, FIEBRE...),
    `raw_text` el fragmento original ("me senti mareada"), `negated` indica si
    aparecia negado ("no tuve dolor"), y `alarm` marca signos de alarma obstetrica
    (varios son datos de preeclampsia). `zones` son las zonas corporales que el NLP
    asocio a este sintoma especifico (docs/integration/nlp-integration.md §1.1)."""

    diary_symptom_id: Optional[int] = None
    patient_diary_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    code: str
    label: Optional[str] = None
    raw_text: Optional[str] = None
    negated: bool = False
    score: Optional[float] = None
    alarm: bool = False
    zones: List[BodyZoneEntity] = []
    model_version: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("zones", mode="before")
    @classmethod
    def _none_zones_to_empty_list(cls, v):
        # Filas creadas antes de agregar la columna `zones` la tienen NULL.
        return v if v is not None else []
