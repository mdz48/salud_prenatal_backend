"""Smoke del slice docs_aggregation + health del gateway."""
import httpx


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "gateway"}


def test_root(client):
    assert client.get("/").status_code == 200


def test_docs_serves_multispec_swagger(client):
    r = client.get("/docs")
    assert r.status_code == 200
    assert "SwaggerUIBundle" in r.text
    assert "StandaloneLayout" in r.text


def test_openapi_unknown_service_is_404(client):
    assert client.get("/api/v1/desconocido/openapi.json").status_code == 404


def test_openapi_service_down_is_503(client):
    # El host docker "usuarios" no resuelve fuera del compose -> error -> 503.
    assert client.get("/api/v1/usuarios/openapi.json").status_code == 503


def test_openapi_rewrites_servers_to_edge(client, monkeypatch):
    def handler(request):
        return httpx.Response(
            200, json={"openapi": "3.1.0", "servers": [{"url": "http://usuarios:8002"}]}
        )

    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: original(transport=transport, **kw)
    )

    r = client.get("/api/v1/usuarios/openapi.json")
    assert r.status_code == 200
    # `servers` reescrito a "/" para que el try-it-out salga por Traefik.
    assert r.json()["servers"] == [{"url": "/"}]
