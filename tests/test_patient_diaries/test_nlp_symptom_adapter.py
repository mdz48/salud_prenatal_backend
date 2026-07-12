import pytest
from unittest.mock import patch, MagicMock

from app.features.patient_diaries.infrastructure.adapters.nlp_symptom_adapter import NlpSymptomAdapter
from app.features.patient_diaries.domain.symptom_extraction_result_entity import SymptomExtractionResult


@pytest.fixture(autouse=True)
def _ml_service_url(monkeypatch):
    monkeypatch.setenv("ML_SERVICE_URL", "http://ml-service:8001/ml")


def test_extract_parses_symptoms_zones_body_zones_y_model_version():
    payload = {
        "symptoms": [
            {
                "code": "MAREO",
                "label": "Mareo",
                "raw_text": "mareada",
                "negated": False,
                "score": 0.9,
                "alarm": False,
                "zones": [{"code": "CABEZA", "label": "Cabeza", "raw_text": "cabeza", "negated": False, "score": 0.8}],
            }
        ],
        "body_zones": [
            {"code": "PIES", "label": "Pies", "raw_text": "hinchados los pies", "negated": False, "score": 0.7}
        ],
        "model_version": "symptemist-onnx-int8",
    }
    mock_response = MagicMock(status_code=200)
    mock_response.json.return_value = payload

    with patch("app.features.patient_diaries.infrastructure.adapters.nlp_symptom_adapter.requests.post", return_value=mock_response):
        result = NlpSymptomAdapter().extract("me siento mareada y con los pies hinchados")

    assert isinstance(result, SymptomExtractionResult)
    assert result.model_version == "symptemist-onnx-int8"
    assert len(result.symptoms) == 1
    assert result.symptoms[0].code == "MAREO"
    assert len(result.symptoms[0].zones) == 1
    assert result.symptoms[0].zones[0].code == "CABEZA"
    assert len(result.body_zones) == 1
    assert result.body_zones[0].code == "PIES"


def test_extract_devuelve_resultado_vacio_en_503():
    mock_response = MagicMock(status_code=503, text="Servicio NLP no disponible")

    with patch("app.features.patient_diaries.infrastructure.adapters.nlp_symptom_adapter.requests.post", return_value=mock_response):
        result = NlpSymptomAdapter().extract("me duele la cabeza")

    assert result == SymptomExtractionResult()


def test_extract_devuelve_resultado_vacio_si_falta_ml_service_url(monkeypatch):
    monkeypatch.delenv("ML_SERVICE_URL", raising=False)

    result = NlpSymptomAdapter().extract("me duele la cabeza")

    assert result == SymptomExtractionResult()


def test_extract_texto_vacio_no_llama_al_servicio():
    with patch("app.features.patient_diaries.infrastructure.adapters.nlp_symptom_adapter.requests.post") as mock_post:
        result = NlpSymptomAdapter().extract("   ")

    mock_post.assert_not_called()
    assert result == SymptomExtractionResult()
