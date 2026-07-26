"""Repo del ledger contra SQLite (DATABASE_URL de test del conftest)."""
import pytest
from sqlalchemy.exc import IntegrityError

from salud_prenatal_shared_core.database import Base, get_engine, get_session_factory
from app.subscriptions.domain.payment_transaction_entity import PaymentTransactionEntity
from app.subscriptions.infrastructure.repositories.payment_transaction_repository import PaymentTransactionRepository


@pytest.fixture()
def session():
    # El import del repo arriba ya registró el modelo en Base.metadata.
    Base.metadata.create_all(bind=get_engine())
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def _tx(event_id="evt_repo_1", user_id=7):
    return PaymentTransactionEntity(
        stripe_event_id=event_id,
        user_id=user_id,
        subscription_id=1,
        kind="payment_succeeded",
        amount_cents=49900,
        currency="mxn",
    )


def test_create_assigns_id_and_exists_finds_it(session):
    repo = PaymentTransactionRepository(session)

    assert repo.exists_by_event_id("evt_repo_1") is False
    created = repo.create(_tx())
    assert created.transaction_id is not None
    assert repo.exists_by_event_id("evt_repo_1") is True


def test_duplicate_event_id_violates_unique(session):
    repo = PaymentTransactionRepository(session)
    repo.create(_tx(event_id="evt_repo_dup"))
    with pytest.raises(IntegrityError):
        repo.create(_tx(event_id="evt_repo_dup"))


def test_list_by_user_id_newest_first(session):
    repo = PaymentTransactionRepository(session)
    repo.create(_tx(event_id="evt_repo_a", user_id=42))
    repo.create(_tx(event_id="evt_repo_b", user_id=42))
    repo.create(_tx(event_id="evt_repo_other", user_id=99))

    result = repo.list_by_user_id(42)

    assert [t.stripe_event_id for t in result] == ["evt_repo_b", "evt_repo_a"]
