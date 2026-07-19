from typing import Optional

from pydantic import BaseModel, ConfigDict


class BodyZoneEntity(BaseModel):
    """Zona corporal mencionada en el texto libre de la bitacora (docs/integration/nlp-integration.md
    §1.1). Comparte forma con ExtractedSymptomEntity pero sin `alarm`: una zona no es en si
    misma un signo de alarma."""

    zone_id: Optional[int] = None
    code: str
    label: Optional[str] = None
    raw_text: Optional[str] = None
    negated: bool = False
    score: Optional[float] = None
    model_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
