import base64
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TEST_DB_DIR = tempfile.mkdtemp(prefix="transaccional_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)

import pytest


@pytest.fixture(scope="session")
def app():
    import main  # dispara create_all en el lifespan al usar TestClient

    return main.app


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session(app):
    # create_all ya corrió al construir el TestClient; aquí abrimos una sesión directa.
    from salud_prenatal_shared_core.database import Base, ReadModelBase, get_engine, get_session_factory

    # Propias (Base) + read-models de users/subscriptions (ReadModelBase) para poder
    # sembrar las tablas ajenas que en producción crean usuarios/pagos.
    Base.metadata.create_all(bind=get_engine())
    ReadModelBase.metadata.create_all(bind=get_engine())
    Session = get_session_factory()
    db = Session()
    try:
        yield db
    finally:
        db.close()
