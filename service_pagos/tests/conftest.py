import base64
import os
import sys
import tempfile
from pathlib import Path

# La raíz del servicio (service_pagos/) debe estar en sys.path para importar
# `main`, `container` y el paquete `app`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Env de test ANTES de importar main / shared_core.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="pagos_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_DIR) / 'test.db'}"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)
# Secret dummy para que el webhook llegue a la verificación de firma de Stripe
# (firma inválida -> InvalidWebhookError -> 400), en vez de fallar por env faltante.
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_dummy")

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
