"""El Key Manager de la llave JWT (port) firma y valida de punta a punta."""
from salud_prenatal_shared_core.jwt_key_provider import (
    get_jwt_key_provider,
    EnvJwtKeyProvider,
    IJwtKeyProvider,
)
from salud_prenatal_shared_core.security import create_access_token
from salud_prenatal_shared_core.auth_dependencies import principal_from_token


def test_provider_activo_es_env_hs256():
    p = get_jwt_key_provider()
    assert isinstance(p, IJwtKeyProvider)
    assert isinstance(p, EnvJwtKeyProvider)
    assert p.algorithm == "HS256"
    # HS256: la llave de firma y la de validación son la misma.
    assert p.get_signing_key() == p.get_verification_key()


def test_firma_y_validacion_pasan_por_el_provider():
    token = create_access_token({"sub": "x@e.com", "user_id": 5, "role": "doctor"})
    principal = principal_from_token(token)
    assert principal is not None
    assert principal.user_id == 5
    assert principal.email == "x@e.com"


def test_token_firmado_con_otra_llave_no_valida(monkeypatch):
    # Firma con la llave actual…
    token = create_access_token({"sub": "x@e.com", "user_id": 1, "role": "paciente"})
    # …cambia la SECRET_KEY y limpia el cache del provider -> ya no valida.
    import salud_prenatal_shared_core.jwt_key_provider as kp
    kp.get_jwt_key_provider.cache_clear()
    monkeypatch.setenv("SECRET_KEY", "otra-llave-distinta")
    try:
        assert principal_from_token(token) is None
    finally:
        kp.get_jwt_key_provider.cache_clear()
