"""Smoke del servicio pagos: health, rutas presentes y auth por claims."""
from salud_prenatal_shared_core.security import create_access_token


def _bearer(**claims):
    return {"Authorization": f"Bearer {create_access_token(claims)}"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "pagos"}


def test_subscription_routes_present(app):
    paths = set(app.openapi()["paths"])
    assert "/api/v1/subscriptions/checkout-session" in paths
    assert "/api/v1/subscriptions/portal-session" in paths
    assert "/api/v1/subscriptions/me" in paths
    assert "/api/v1/subscriptions/webhook" in paths


def test_me_requires_auth(client):
    assert client.get("/api/v1/subscriptions/me").status_code == 401


def test_me_forbidden_for_non_doctor(client):
    r = client.get(
        "/api/v1/subscriptions/me",
        headers=_bearer(sub="p@e.com", user_id=1, role="paciente"),
    )
    assert r.status_code == 403


def test_me_doctor_returns_pending_when_no_row(client):
    # Ejercita DB + repo + use case + controller: doctor sin fila -> pending.
    r = client.get(
        "/api/v1/subscriptions/me",
        headers=_bearer(sub="d@e.com", user_id=99, role="doctor", subscription_status=None),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


def test_webhook_without_signature_is_rejected(client):
    # Sin firma válida de Stripe -> 400 (InvalidWebhookError). No requiere auth.
    r = client.post("/api/v1/subscriptions/webhook", content=b"{}")
    assert r.status_code == 400
