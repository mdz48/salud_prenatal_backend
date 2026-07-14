from types import SimpleNamespace

from app.features.medical_record.infrastructure.adapters.ml_prediction_adapter import (
    MlPredictionServiceAdapter,
)


def _patient(age=30):
    return SimpleNamespace(age=age)


def _record(initial_systolic=None, initial_diastolic=None):
    # Solo los campos que build_payload lee; el resto en valores neutros.
    return SimpleNamespace(
        initial_weight=60.0,
        height_cm=160,
        current_gestational_weeks=12,
        education_level="superior",
        residence="urbana",
        marital_status="married",
        initial_systolic=initial_systolic,
        initial_diastolic=initial_diastolic,
        previous_deliveries=0,
        diabetes=False,
        chronic_hypertension=False,
        previous_preeclampsia=False,
        family_history_hypertension=False,
        family_history_heart_disease=False,
        chronic_kidney_disease=False,
        multiple_pregnancy=False,
        active_smoking=False,
        previous_pregnancies=0,
        previous_miscarriages=0,
        previous_cesareans=0,
    )


def _diary(systolic=None, diastolic=None, weight_kg=None, weight_gain=None):
    return SimpleNamespace(
        systolic=systolic, diastolic=diastolic, weight_kg=weight_kg, weight_gain=weight_gain
    )


def test_usa_presion_basal_del_expediente_sin_bitacora():
    adapter = MlPredictionServiceAdapter()
    payload = adapter.build_payload(_patient(), _record(initial_systolic=118, initial_diastolic=76), None)

    assert payload["systolic"] == 118.0
    assert payload["diastolic"] == 76.0
    # MAP = (118 + 2*76) / 3 = 90.0
    assert payload["mean_arterial_pressure"] == 90.0


def test_bitacora_tiene_prioridad_sobre_la_basal():
    adapter = MlPredictionServiceAdapter()
    record = _record(initial_systolic=118, initial_diastolic=76)
    diary = _diary(systolic=150, diastolic=95, weight_kg=65.0)

    payload = adapter.build_payload(_patient(), record, diary)

    assert payload["systolic"] == 150.0
    assert payload["diastolic"] == 95.0
    # MAP = (150 + 2*95) / 3 = 113.33
    assert payload["mean_arterial_pressure"] == 113.33


def test_sin_bitacora_y_sin_basal_es_cero_seguro():
    adapter = MlPredictionServiceAdapter()
    payload = adapter.build_payload(_patient(), _record(), None)

    assert payload["systolic"] == 0.0
    assert payload["diastolic"] == 0.0
    assert payload["mean_arterial_pressure"] == 0.0
