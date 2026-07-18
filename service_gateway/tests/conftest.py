import os
import sys
from pathlib import Path

# La raíz del servicio (service_gateway/) debe estar en sys.path para importar
# `main` y el paquete `features`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Env de test ANTES de importar main / shared_core. El validador no usa DB;
# solo necesita la llave para verificar los JWTs que fabrican los tests.
os.environ.setdefault("SECRET_KEY", "test-secret")

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
