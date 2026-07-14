from datetime import datetime

from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.features.patient_diaries.domain.body_zone_entity import BodyZoneEntity
from app.features.patient_diaries.domain.symptom_aggregation import aggregate_symptoms, AggregatedSymptom


def _sym(code, created_at, negated=False, alarm=False, label=None, zones=None):
    return ExtractedSymptomEntity(
        code=code, label=label, negated=negated, alarm=alarm, created_at=created_at,
        zones=[BodyZoneEntity(code=z) for z in (zones or [])],
    )


def test_agrupa_por_code_con_conteo_y_rango_de_fechas():
    symptoms = [
        _sym("SANGRADO", datetime(2026, 6, 20, 8, 0), alarm=True, label="Sangrado", zones=["ABDOMEN"]),
        _sym("SANGRADO", datetime(2026, 6, 23, 9, 0), zones=["ABDOMEN", "PELVIS"]),
        _sym("CEFALEA", datetime(2026, 6, 22, 8, 0), label="Cefalea"),
    ]

    result = aggregate_symptoms(symptoms)

    by_code = {a.code: a for a in result}
    assert by_code["SANGRADO"].occurrences == 2
    assert by_code["SANGRADO"].first_seen == datetime(2026, 6, 20, 8, 0)
    assert by_code["SANGRADO"].last_seen == datetime(2026, 6, 23, 9, 0)
    assert by_code["SANGRADO"].alarm is True
    assert by_code["SANGRADO"].label == "Sangrado"
    assert sorted(by_code["SANGRADO"].zones) == ["ABDOMEN", "PELVIS"]  # dedup
    assert by_code["CEFALEA"].occurrences == 1


def test_excluye_negados():
    symptoms = [
        _sym("DOLOR", datetime(2026, 6, 20, 8, 0), negated=True),
        _sym("MAREO", datetime(2026, 6, 21, 8, 0)),
    ]

    result = aggregate_symptoms(symptoms)

    assert [a.code for a in result] == ["MAREO"]


def test_orden_alarma_primero_luego_mas_reciente():
    symptoms = [
        _sym("VIEJO_NO_ALARMA", datetime(2026, 6, 1, 8, 0)),
        _sym("RECIENTE_NO_ALARMA", datetime(2026, 6, 25, 8, 0)),
        _sym("ALARMA", datetime(2026, 6, 10, 8, 0), alarm=True),
    ]

    result = aggregate_symptoms(symptoms)

    assert [a.code for a in result] == ["ALARMA", "RECIENTE_NO_ALARMA", "VIEJO_NO_ALARMA"]


def test_lista_vacia_devuelve_vacio():
    assert aggregate_symptoms([]) == []
