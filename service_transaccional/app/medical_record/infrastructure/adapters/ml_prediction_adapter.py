import os
import requests
from dotenv import load_dotenv
from app.medical_record.domain.ports import IMLPredictionService
from app.medical_record.domain.risk_features import build_ml_payload

load_dotenv()

class MlPredictionServiceAdapter(IMLPredictionService):
    """Transporte HTTP hacia el microservicio ML. El feature engineering vive en
    domain/risk_features.py; aqui solo se arma la peticion y se maneja el fallo."""

    def build_payload(self, patient, medical_record, latest_diary: object) -> dict:
        return build_ml_payload(patient, medical_record, latest_diary)

    def predict(self, patient, medical_record, latest_diary) -> dict | None:
        ml_service_url = os.getenv("ML_SERVICE_URL")
        if not ml_service_url:
            return None

        payload = self.build_payload(patient, medical_record, latest_diary)
        try:
            response = requests.post(f"{ml_service_url}/predict", json=payload, timeout=2.0)
            if response.status_code == 200:
                return response.json()
            print("ML Service returned non-200:", response.status_code, response.text)
        except Exception as e:
            print("ML Service Exception:", str(e))

        return None
