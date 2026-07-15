from types import SimpleNamespace

from app.features.medical_record.domain.risk_features import assess_completeness, effective_pressure


def _patient(age=30):
    return SimpleNamespace(age=age)


def _record(height_cm=160, initial_weight=60.0, initial_systolic=118, initial_diastolic=76):
    return SimpleNamespace(
        height_cm=height_cm,
        initial_weight=initial_weight,
        initial_systolic=initial_systolic,
        initial_diastolic=initial_diastolic,
    )


def _diary(systolic=None, diastolic=None):
    return SimpleNamespace(systolic=systolic, diastolic=diastolic)


def test_todo_presente_es_suficiente():
    assert assess_completeness(_patient(), _record(), None) == []


def test_sin_edad():
    assert assess_completeness(_patient(age=None), _record(), None) == ["age"]


def test_sin_talla_ni_peso():
    missing = assess_completeness(_patient(), _record(height_cm=None, initial_weight=None), None)
    assert missing == ["height_cm", "initial_weight"]


def test_sin_presion_basal_ni_bitacora():
    missing = assess_completeness(
        _patient(), _record(initial_systolic=None, initial_diastolic=None), None
    )
    assert missing == ["systolic", "diastolic"]


def test_bitacora_cubre_la_falta_de_basal():
    record = _record(initial_systolic=None, initial_diastolic=None)
    assert assess_completeness(_patient(), record, _diary(systolic=120, diastolic=80)) == []


def test_effective_pressure_prioriza_bitacora():
    assert effective_pressure(_record(), _diary(systolic=150, diastolic=95)) == (150, 95)
    assert effective_pressure(_record(), None) == (118, 76)
