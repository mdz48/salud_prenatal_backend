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
