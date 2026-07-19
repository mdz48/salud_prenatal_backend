from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .extracted_symptom_entity import ExtractedSymptomEntity
from .body_zone_entity import BodyZoneEntity


class SymptomExtractionResult(BaseModel):
    """Resultado crudo de POST /nlp/extract-symptoms (docs/integration/nlp-integration.md §1.1).
    Contenedor devuelto por ISymptomExtractionPort.extract(); vacio por defecto para que el
    fallo del NLP degrade limpio sin distinguir 503/timeout/texto vacio en el llamador."""

    symptoms: List[ExtractedSymptomEntity] = []
    body_zones: List[BodyZoneEntity] = []
    model_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
