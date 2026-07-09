import base64
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Env de test debe quedar definido ANTES de importar main/app.core.*
_TEST_DB_DIR = tempfile.mkdtemp(prefix="salud_prenatal_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
os.environ.setdefault("SECRET_KEY", "test-secret")
# Fernet key valida y fija (32 bytes '0' en urlsafe base64), solo para tests
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)

import pytest


@pytest.fixture(scope="session")
def app():
    import main  # importa con env de test ya seteado; create_all corre contra SQLite

    return main.app


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def activate_subscription(app):
    """Activa la suscripcion de un doctor escribiendo directo en la BD de test,
    sin pasar por Stripe. Los doctores quedan 'pending' al registrarse, asi que
    los flujos e2e que ejercitan endpoints gateados deben activarla primero."""
    from app.core.database import get_session_factory
    from app.features.users.infrastructure.models.user_model import Usuario
    from app.features.subscriptions.infrastructure.models.subscription_model import Subscription
    from app.core.enums import SubscriptionStatusEnum

    def _activate(email: str):
        db = get_session_factory()()
        try:
            user = db.query(Usuario).filter(Usuario.email == email).first()
            assert user is not None, f"No user for email {email}"
            sub = db.query(Subscription).filter(Subscription.user_id == user.user_id).first()
            assert sub is not None, f"No subscription row for user {user.user_id}"
            sub.status = SubscriptionStatusEnum.active
            db.commit()
        finally:
            db.close()

    return _activate
