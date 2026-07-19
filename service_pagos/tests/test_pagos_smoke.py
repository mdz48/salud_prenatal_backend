"""Smoke del servicio pagos: health, rutas presentes y auth por headers del edge."""


def _headers(**claims):
    """Identidad como la inyecta el ForwardAuth del gateway tras validar el JWT.
    Los claims se nombran igual que antes para no reescribir cada test."""
    return {
        "X-User-Id": str(claims.get("user_id", "")),
        "X-User-Email": claims.get("sub", ""),
        "X-User-Role": claims.get("role", ""),
        "X-Subscription-Status": claims.get("subscription_status") or "",
    }


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
        headers=_headers(sub="p@e.com", user_id=1, role="paciente"),
    )
    assert r.status_code == 403


def test_me_doctor_returns_pending_when_no_row(client):
    # Ejercita DB + repo + use case + controller: doctor sin fila -> pending.
    r = client.get(
        "/api/v1/subscriptions/me",
        headers=_headers(sub="d@e.com", user_id=99, role="doctor", subscription_status=None),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


def test_webhook_without_signature_is_rejected(client):
    # Sin firma válida de Stripe -> 400 (InvalidWebhookError). No requiere auth.
    r = client.post("/api/v1/subscriptions/webhook", content=b"{}")
    assert r.status_code == 400


def test_payments_route_present(app):
    assert "/api/v1/subscriptions/payments" in set(app.openapi()["paths"])


def test_payments_requires_auth(client):
    assert client.get("/api/v1/subscriptions/payments").status_code == 401


def test_payments_forbidden_for_non_doctor(client):
    r = client.get(
        "/api/v1/subscriptions/payments",
        headers=_headers(sub="p@e.com", user_id=1, role="paciente"),
    )
    assert r.status_code == 403


def test_payments_doctor_without_history_gets_empty_list(client):
    # user_id sin filas en el ledger -> lista vacía (ejercita DB + repo + use case).
    r = client.get(
        "/api/v1/subscriptions/payments",
        headers=_headers(sub="d@e.com", user_id=54321, role="doctor"),
    )
    assert r.status_code == 200
    assert r.json() == []
