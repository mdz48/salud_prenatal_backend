"""El WS del chat autentica por el header X-User-Id que inyecta el edge.

El JWT ya se validó UNA vez en el ForwardAuth del gateway (que para el upgrade
lee `?token=` de X-Forwarded-Uri). Aquí solo se confía en el header.
"""
import pytest
from fastapi import WebSocketDisconnect

WS_URL = "/api/v1/chat/ws"


def test_ws_connects_with_identity_header(client):
    with client.websocket_connect(WS_URL, headers={"X-User-Id": "1"}) as ws:
        assert ws is not None


def test_ws_without_identity_header_is_rejected(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(WS_URL):
            pass
    assert exc.value.code == 1008


def test_ws_with_empty_identity_header_is_rejected(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(WS_URL, headers={"X-User-Id": ""}):
            pass
    assert exc.value.code == 1008


def test_ws_with_non_numeric_identity_header_is_rejected(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(WS_URL, headers={"X-User-Id": "abc"}):
            pass
    assert exc.value.code == 1008
