import base64
import os
import sys
import tempfile
from pathlib import Path

# Raíz del servicio (service_usuarios/) en sys.path para importar main/container/app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Env de test ANTES de importar main / shared_core.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="usuarios_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)

import pytest


@pytest.fixture(scope="session")
def app():
    import main

    return main.app


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
