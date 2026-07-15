"""Smoke tests del servicio auth (Sesión 5)."""
from jose import jwt

from salud_prenatal_shared_core.security import get_secret_key, ALGORITHM


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "auth"}


def test_login_route_exists(app):
    paths = app.openapi()["paths"]
    assert "/api/v1/users/login" in paths, "el login debe conservar el path del monolito"


def test_login_ok_emits_jwt_with_claims(client, seed_user):
    creds = seed_user(email="doc1@example.com", password="secret123")

    r = client.post(
        "/api/v1/users/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["token_type"] == "bearer"
    assert body["user_id"] == creds["user_id"]
    assert body["role"] == "doctor"
    # Doctor sin fila de suscripción -> status None (pagos lo tratará como pending).
    assert body["subscription_status"] is None

    # El token lleva los claims que los demás servicios necesitan para autorizar.
    payload = jwt.decode(body["access_token"], get_secret_key(), algorithms=[ALGORITHM])
    assert payload["sub"] == creds["email"]
    assert payload["user_id"] == creds["user_id"]
    assert payload["role"] == "doctor"
    assert "subscription_status" in payload


def test_login_wrong_password_401(client, seed_user):
    seed_user(email="doc2@example.com", password="secret123")
    r = client.post(
        "/api/v1/users/login",
        json={"email": "doc2@example.com", "password": "WRONG"},
    )
    assert r.status_code == 401


def test_login_accepts_form_urlencoded(client, seed_user):
    creds = seed_user(email="doc3@example.com", password="secret123")
    r = client.post(
        "/api/v1/users/login",
        data={"username": creds["email"], "password": creds["password"]},
    )
    assert r.status_code == 200, r.text
    assert r.json()["access_token"]
