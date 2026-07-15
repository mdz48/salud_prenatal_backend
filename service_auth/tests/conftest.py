import base64
import os
import sys
import tempfile
from pathlib import Path

# Raíz del servicio (service_auth/) en sys.path para importar main/container/app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Env de test ANTES de importar main / shared_core.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="auth_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)

import pytest


@pytest.fixture(scope="session")
def app():
    import main

    # auth NO hace create_all (no es dueño del schema): todos sus modelos son
    # read-models sobre ReadModelBase. En test creamos ese schema para poder
    # sembrar/leer las tablas que en producción crea el servicio dueño.
    from salud_prenatal_shared_core.database import ReadModelBase, get_engine

    ReadModelBase.metadata.create_all(bind=get_engine())
    return main.app


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def seed_user():
    """Inserta un usuario en la DB de test y devuelve sus credenciales.

    Usa los read-models de auth para escribir directo (en la app real esta fila la
    crea el servicio usuarios; aquí simulamos ese estado de la DB compartida).
    """
    from salud_prenatal_shared_core.database import get_session_factory
    from salud_prenatal_shared_core.security import get_password_hash
    from salud_prenatal_shared_core.enums import RoleEnum
    from app.auth.infrastructure.models.auth_readmodels import UserAuth

    def _create(email="doc@example.com", password="secret123", role=RoleEnum.doctor,
                is_active=True):
        Session = get_session_factory()
        db = Session()
        try:
            user = UserAuth(
                name="Ada",
                last_name="Lovelace",
                email=email,
                password=get_password_hash(password),
                role=role,
                is_active=is_active,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"email": email, "password": password, "user_id": user.user_id,
                    "role": role.value}
        finally:
            db.close()

    return _create
