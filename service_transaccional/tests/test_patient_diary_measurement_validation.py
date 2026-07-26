from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.patient_diaries.domain.diary_validation import validate_diary_measurements


def _entity(weight_kg=70.0, systolic=120, diastolic=80):
    return PatientDiaryEntity(
        medical_record_id=1,
        weight_kg=weight_kg,
        systolic=systolic,
        diastolic=diastolic,
    )


def test_valid_measurements_produce_no_errors():
    notification = validate_diary_measurements(_entity())

    assert notification.has_errors() is False


def test_weight_out_of_range_is_rejected():
    notification = validate_diary_measurements(_entity(weight_kg=5.0))

    assert notification.has_errors() is True
    assert any("peso" in e.lower() for e in notification.errors)


def test_systolic_out_of_range_is_rejected():
    notification = validate_diary_measurements(_entity(systolic=350))

    assert notification.has_errors() is True
    assert any("sistólica" in e.lower() for e in notification.errors)


def test_diastolic_out_of_range_is_rejected():
    notification = validate_diary_measurements(_entity(diastolic=5))

    assert notification.has_errors() is True
    assert any("diastólica" in e.lower() for e in notification.errors)


def test_systolic_must_be_greater_than_diastolic():
    notification = validate_diary_measurements(_entity(systolic=80, diastolic=90))

    assert notification.has_errors() is True
    assert any("sistólica" in e.lower() and "diastólica" in e.lower() for e in notification.errors)


def test_accumulates_all_violations_at_once():
    notification = validate_diary_measurements(_entity(weight_kg=1000.0, systolic=400, diastolic=1))

    assert len(notification.errors) == 3


def test_none_fields_are_skipped_for_partial_updates():
    entity = PatientDiaryEntity(medical_record_id=1, weight_kg=None, systolic=None, diastolic=None)

    notification = validate_diary_measurements(entity)

    assert notification.has_errors() is False
