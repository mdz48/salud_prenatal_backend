import os

import requests
from dotenv import load_dotenv

from app.patient_diaries.domain.ports import ISymptomExtractionPort
from app.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.patient_diaries.domain.body_zone_entity import BodyZoneEntity
from app.patient_diaries.domain.symptom_extraction_result_entity import SymptomExtractionResult

load_dotenv()


class NlpSymptomAdapter(ISymptomExtractionPort):
    """Gateway HTTP al endpoint /nlp/extract-symptoms del microservicio ML (ADR-14,
    Strategy: hoy la estrategia es el pipeline transformer remoto). Falla en silencio
    devolviendo un SymptomExtractionResult vacio para que la bitacora nunca se
    bloquee si el NLP esta caido o lento."""

    def extract(self, text: str) -> SymptomExtractionResult:
        if not text or not text.strip():
            return SymptomExtractionResult()

        ml_service_url = os.getenv("ML_SERVICE_URL")
        if not ml_service_url:
            return SymptomExtractionResult()

        try:
            response = requests.post(
                f"{ml_service_url}/nlp/extract-symptoms",
                json={"text": text},
                timeout=float(os.getenv("NLP_TIMEOUT", "8.0")),
            )
            if response.status_code == 200:
                data = response.json()
                return SymptomExtractionResult(
                    symptoms=[ExtractedSymptomEntity(**s) for s in data.get("symptoms", [])],
                    body_zones=[BodyZoneEntity(**z) for z in data.get("body_zones", [])],
                    model_version=data.get("model_version"),
                )
            print("NLP Service returned non-200:", response.status_code, response.text)
        except Exception as e:
            print("NLP Service Exception:", str(e))

        return SymptomExtractionResult()
