"""Contrato del validador ForwardAuth: /validate (lenient) y /validate/strict."""
from datetime import timedelta

from salud_prenatal_shared_core.security import create_access_token
from salud_prenatal_shared_core.auth_dependencies import IDENTITY_HEADERS


def _token(**claims):
    return create_access_token(data=claims)


class TestValidateLenient:
    def test_anonymous_returns_200_with_all_identity_headers_empty(self, client):
        r = client.get("/validate")
        assert r.status_code == 200
        # Presentes Y vacíos: anti-spoofing. Traefik solo borra-y-copia los
        # headers que el validador emite; omitir uno dejaría pasar el del cliente.
        for header in IDENTITY_HEADERS:
            assert r.headers[header] == ""

    def test_valid_bearer_populates_identity(self, client):
        token = _token(
            sub="d@e.com", user_id=7, role="doctor",
            subscription_status="active",
            subscription_current_period_end="2026-08-15T12:00:00",
        )
        r = client.get("/validate", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.headers["X-User-Id"] == "7"
        assert r.headers["X-User-Email"] == "d@e.com"
        assert r.headers["X-User-Role"] == "doctor"
        assert r.headers["X-Subscription-Status"] == "active"
        assert r.headers["X-Subscription-Period-End"].startswith("2026-08-15")

    def test_garbage_bearer_is_401(self, client):
        r = client.get("/validate", headers={"Authorization": "Bearer basura"})
        assert r.status_code == 401

    def test_expired_bearer_is_401(self, client):
        token = create_access_token(
            data={"sub": "d@e.com", "user_id": 1},
            expires_delta=timedelta(minutes=-1),
        )
        r = client.get("/validate", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_non_bearer_scheme_is_anonymous(self, client):
        r = client.get("/validate", headers={"Authorization": "Basic abc123"})
        assert r.status_code == 200
        assert r.headers["X-User-Email"] == ""

    def test_forwarded_uri_query_token_valid(self, client):
        # Vía de auth del upgrade del WebSocket: Traefik manda la URI original.
        token = _token(sub="d@e.com", user_id=1)
        r = client.get(
            "/validate",
            headers={"X-Forwarded-Uri": f"/api/v1/chat/ws?token={token}"},
        )
        assert r.status_code == 200
        assert r.headers["X-User-Id"] == "1"

    def test_forwarded_uri_query_token_invalid_is_401(self, client):
        r = client.get(
            "/validate",
            headers={"X-Forwarded-Uri": "/api/v1/chat/ws?token=basura"},
        )
        assert r.status_code == 401

    def test_bearer_wins_over_query_token(self, client):
        bearer = _token(sub="bearer@e.com", user_id=1)
        query = _token(sub="query@e.com", user_id=2)
        r = client.get(
            "/validate",
            headers={
                "Authorization": f"Bearer {bearer}",
                "X-Forwarded-Uri": f"/api/v1/chat/ws?token={query}",
            },
        )
        assert r.status_code == 200
        assert r.headers["X-User-Email"] == "bearer@e.com"


class TestValidateStrict:
    def test_anonymous_is_401(self, client):
        assert client.get("/validate/strict").status_code == 401

    def test_valid_bearer_is_200_with_identity(self, client):
        token = _token(sub="d@e.com", user_id=7, role="doctor")
        r = client.get("/validate/strict", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.headers["X-User-Id"] == "7"

    def test_query_token_is_200(self, client):
        token = _token(sub="d@e.com", user_id=7)
        r = client.get(
            "/validate/strict",
            headers={"X-Forwarded-Uri": f"/api/v1/chat/ws?token={token}"},
        )
        assert r.status_code == 200

    def test_garbage_bearer_is_401(self, client):
        r = client.get("/validate/strict", headers={"Authorization": "Bearer basura"})
        assert r.status_code == 401
