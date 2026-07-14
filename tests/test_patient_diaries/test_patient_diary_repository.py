from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base (mappers y create_all)
from app.core.database import Base
from app.features.patient_diaries.infrastructure.models.patient_diaries_model import PatientDiary
from app.features.patient_diaries.infrastructure.repositories.patient_diary_repository import (
    PatientDiaryRepository,
)
from app.features.patient_diaries.infrastructure.repositories.diary_symptom_extraction_repository import (
    DiarySymptomExtractionRepository,
)
from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.features.patient_diaries.domain.body_zone_entity import BodyZoneEntity
from app.features.patient_diaries.domain.symptom_extraction_result_entity import SymptomExtractionResult


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _insert(session, medical_record_id, created_at, **fields):
    row = PatientDiary(medical_record_id=medical_record_id, created_at=created_at, **fields)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def test_get_latest_devuelve_la_bitacora_mas_reciente(db_session):
    repo = PatientDiaryRepository(db_session)
    _insert(db_session, 1, datetime(2026, 7, 1, 8, 0), systolic=110, diastolic=70, weight_kg=60.0)
    reciente = _insert(db_session, 1, datetime(2026, 7, 5, 8, 0), systolic=130, diastolic=85, weight_kg=63.0)
    # Bitacora de otro expediente: no debe interferir
    _insert(db_session, 2, datetime(2026, 7, 9, 8, 0), systolic=120, diastolic=80)

    latest = repo.get_latest_by_medical_record_id(1)

    assert latest is not None
    assert latest.patient_diary_id == reciente.patient_diary_id
    assert latest.systolic == 130
    assert latest.diastolic == 85
    assert latest.weight_kg == 63.0


def test_get_latest_desempata_por_id_con_timestamps_iguales(db_session):
    repo = PatientDiaryRepository(db_session)
    mismo_instante = datetime(2026, 7, 5, 8, 0)
    _insert(db_session, 1, mismo_instante, systolic=110)
    segunda = _insert(db_session, 1, mismo_instante, systolic=140)

    latest = repo.get_latest_by_medical_record_id(1)

    assert latest.patient_diary_id == segunda.patient_diary_id
    assert latest.systolic == 140


def test_get_latest_sin_bitacoras_devuelve_none(db_session):
    assert PatientDiaryRepository(db_session).get_latest_by_medical_record_id(999) is None


def test_replace_for_diary_persiste_zones_body_zones_y_model_version(db_session):
    repo = DiarySymptomExtractionRepository(db_session)
    result = SymptomExtractionResult(
        symptoms=[
            ExtractedSymptomEntity(
                code="MAREO",
                raw_text="mareada",
                zones=[BodyZoneEntity(code="CABEZA", raw_text="cabeza")],
            )
        ],
        body_zones=[BodyZoneEntity(code="PIES", raw_text="hinchados los pies")],
        model_version="symptemist-onnx-int8",
    )

    saved = repo.replace_for_diary(patient_diary_id=1, medical_record_id=10, result=result)

    assert len(saved) == 1
    assert saved[0].code == "MAREO"
    assert saved[0].zones[0].code == "CABEZA"
    assert saved[0].model_version == "symptemist-onnx-int8"

    persisted_zones = repo.get_body_zones_by_diary_id(1)
    assert len(persisted_zones) == 1
    assert persisted_zones[0].code == "PIES"
    assert persisted_zones[0].model_version == "symptemist-onnx-int8"


def test_replace_for_diary_es_idempotente(db_session):
    repo = DiarySymptomExtractionRepository(db_session)
    primero = SymptomExtractionResult(symptoms=[ExtractedSymptomEntity(code="MAREO")], body_zones=[BodyZoneEntity(code="PIES")])
    segundo = SymptomExtractionResult(symptoms=[ExtractedSymptomEntity(code="CEFALEA")], body_zones=[])

    repo.replace_for_diary(patient_diary_id=1, medical_record_id=10, result=primero)
    repo.replace_for_diary(patient_diary_id=1, medical_record_id=10, result=segundo)

    assert [s.code for s in repo.get_by_diary_id(1)] == ["CEFALEA"]
    assert repo.get_body_zones_by_diary_id(1) == []


def test_get_by_medical_record_id_filtra_por_since(db_session):
    from datetime import datetime
    from app.features.patient_diaries.infrastructure.models.diary_symptom_extraction_model import DiarySymptomExtraction

    def _add(code, created_at):
        db_session.add(DiarySymptomExtraction(
            patient_diary_id=1, medical_record_id=10, code=code, created_at=created_at,
        ))

    _add("VIEJO", datetime(2026, 6, 1, 8, 0))
    _add("NUEVO", datetime(2026, 6, 10, 8, 0))
    db_session.commit()

    repo = DiarySymptomExtractionRepository(db_session)

    corte = datetime(2026, 6, 5, 8, 0)
    solo_nuevos = repo.get_by_medical_record_id(10, since=corte)
    assert [s.code for s in solo_nuevos] == ["NUEVO"]

    todos = repo.get_by_medical_record_id(10)
    assert {s.code for s in todos} == {"VIEJO", "NUEVO"}
