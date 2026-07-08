import os
from typing import List

import requests
from dotenv import load_dotenv

from app.features.patient_diaries.domain.ports import ISymptomExtractionPort
from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity

load_dotenv()


class NlpSymptomAdapter(ISymptomExtractionPort):
    """Gateway HTTP al endpoint /nlp/extract-symptoms del microservicio ML (ADR-14,
    Strategy: hoy la estrategia es el pipeline transformer remoto). Falla en silencio
    devolviendo [] para que la bitacora nunca se bloquee si el NLP esta caido o lento."""

    def extract(self, text: str) -> List[ExtractedSymptomEntity]:
        if not text or not text.strip():
            return []

        ml_service_url = os.getenv("ML_SERVICE_URL")
        if not ml_service_url:
            return []

        try:
            response = requests.post(
                f"{ml_service_url}/nlp/extract-symptoms",
                json={"text": text},
                timeout=float(os.getenv("NLP_TIMEOUT", "8.0")),
            )
            if response.status_code == 200:
                data = response.json()
                return [ExtractedSymptomEntity(**s) for s in data.get("symptoms", [])]
            print("NLP Service returned non-200:", response.status_code, response.text)
        except Exception as e:
            print("NLP Service Exception:", str(e))

        return []
