from datetime import date

from salud_prenatal_shared_core.database import Base, ReadModelBase, get_engine, get_session_factory
from app.users.infrastructure.models.patient_model import Patient
from app.users.infrastructure.models.user_model import Usuario
from app.users.infrastructure.models import doctor_model, receptionist_model  # noqa: F401
from app.users.infrastructure.readmodels.social_profile_readmodel import SocialProfileRead
from app.users.infrastructure.adapters.risk_cluster_filter_adapter import RiskClusterFilterAdapter
from salud_prenatal_shared_core.enums import RoleEnum


def setup_test_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    ReadModelBase.metadata.create_all(bind=engine)
    return get_session_factory()()


def _make_patient(db, email, doctor_id):
    user = Usuario(name="N", last_name="L", email=email, password="x", role=RoleEnum.patient, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    patient = Patient(user_id=user.user_id, doctor_id=doctor_id, birthdate=date(2000, 1, 1))
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def test_returns_patient_ids_matching_cluster_scoped_to_doctor():
    db = setup_test_db()
    try:
        p1 = _make_patient(db, "h1@test.com", doctor_id=910001)
        p2 = _make_patient(db, "h2@test.com", doctor_id=910001)
        p3 = _make_patient(db, "h3@test.com", doctor_id=910002)  # otro doctor, mismo cluster

        db.add_all([
            SocialProfileRead(user_id=p1.user_id, cluster_profile="alto"),
            SocialProfileRead(user_id=p2.user_id, cluster_profile="bajo"),
            SocialProfileRead(user_id=p3.user_id, cluster_profile="alto"),
        ])
        db.commit()

        adapter = RiskClusterFilterAdapter(db=db)
        result = adapter.get_patient_ids_by_risk_cluster(doctor_id=910001, risk_cluster="alto")

        assert result == [p1.patient_id]
    finally:
        db.close()


def test_patients_without_social_profile_are_excluded():
    db = setup_test_db()
    try:
        _make_patient(db, "h4@test.com", doctor_id=910003)  # nunca creo perfil social

        adapter = RiskClusterFilterAdapter(db=db)
        result = adapter.get_patient_ids_by_risk_cluster(doctor_id=910003, risk_cluster="alto")

        assert result == []
    finally:
        db.close()


def test_returns_empty_when_no_match_for_cluster():
    db = setup_test_db()
    try:
        p1 = _make_patient(db, "h5@test.com", doctor_id=910004)
        db.add(SocialProfileRead(user_id=p1.user_id, cluster_profile="bajo"))
        db.commit()

        adapter = RiskClusterFilterAdapter(db=db)
        result = adapter.get_patient_ids_by_risk_cluster(doctor_id=910004, risk_cluster="alto")

        assert result == []
    finally:
        db.close()
