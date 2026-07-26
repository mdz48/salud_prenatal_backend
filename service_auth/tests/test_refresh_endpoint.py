import pytest
from jose import jwt

from salud_prenatal_shared_core.enums import SubscriptionStatusEnum
from salud_prenatal_shared_core.jwt_key_provider import get_jwt_key_provider


def _set_subscription_status(user_id: int, status: SubscriptionStatusEnum):
    from salud_prenatal_shared_core.database import get_session_factory
    from app.auth.infrastructure.models.auth_readmodels import SubscriptionAuth

    Session = get_session_factory()
    db = Session()
    try:
        sub = db.query(SubscriptionAuth).filter(SubscriptionAuth.user_id == user_id).first()
        if not sub:
            sub = SubscriptionAuth(user_id=user_id, status=status)
            db.add(sub)
        else:
            sub.status = status
        db.commit()
    finally:
        db.close()


def _decode(token):
    p = get_jwt_key_provider()
    return jwt.decode(token, p.get_verification_key(), algorithms=[p.algorithm])


def _headers(user):
    """Identidad como la inyecta el edge (ForwardAuth) tras validar el Bearer.
    El servicio ya no decodifica el token: solo lee estos headers."""
    return {
        "X-User-Id": str(user["user_id"]),
        "X-User-Email": user["email"],
        "X-User-Role": user["role"],
    }


def test_refresh_token_endpoint(client, seed_user):
    # 1. Crear un doctor
    user = seed_user(role=pytest.importorskip("salud_prenatal_shared_core.enums").RoleEnum.doctor)
    
    # 2. Setear su suscripción a pending
    _set_subscription_status(user["user_id"], SubscriptionStatusEnum.pending)

    # 3. Login original -> Token dice pending
    res_login = client.post(
        "/api/v1/users/login",
        json={"email": user["email"], "password": user["password"]}
    )
    assert res_login.status_code == 200, res_login.json()
    old_token = res_login.json()["access_token"]
    assert _decode(old_token)["subscription_status"] == "pending"

    # 4. Simular que paga -> DB pasa a active
    _set_subscription_status(user["user_id"], SubscriptionStatusEnum.active)

    # 5. Llamar refresh con la identidad que inyectaría el edge tras validar el
    #    token viejo. El use case relee el status FRESCO de la DB: por eso el
    #    token nuevo dice active aunque el viejo dijera pending.
    res_refresh = client.post(
        "/api/v1/users/refresh",
        headers=_headers(user),
    )

    assert res_refresh.status_code == 200
    data = res_refresh.json()
    assert data["subscription_status"] == "active"
    
    new_token = data["access_token"]
    assert new_token != old_token
    assert _decode(new_token)["subscription_status"] == "active"


def test_refresh_token_unauthorized(client):
    res = client.post("/api/v1/users/refresh")
    # Sin identidad inyectada -> 401. En producción el request ni llega: el
    # router de refresh lleva el middleware estricto (jwt-strict) en Traefik.
    assert res.status_code == 401
