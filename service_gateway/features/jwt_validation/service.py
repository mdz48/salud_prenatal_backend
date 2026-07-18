"""Caso de uso del validador ForwardAuth: extraer token, verificar, serializar
la identidad al contrato de headers X-User-*. Lógica pura, sin FastAPI."""
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from salud_prenatal_shared_core.auth_dependencies import (
    HEADER_SUBSCRIPTION_PERIOD_END,
    HEADER_SUBSCRIPTION_STATUS,
    HEADER_USER_EMAIL,
    HEADER_USER_ID,
    HEADER_USER_ROLE,
    IDENTITY_HEADERS,
    Principal,
)

from .ports import ITokenVerifier


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Token del header Authorization. None si falta o el esquema no es Bearer
    (paridad con el gateway anterior: esquemas ajenos se tratan como anónimo)."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def extract_query_token(forwarded_uri: Optional[str]) -> Optional[str]:
    """Token de `?token=` en X-Forwarded-Uri. Traefik manda al validador la URI
    original del request (el query del WS NO llega como query de /validate);
    es la vía de autenticación del upgrade del WebSocket del chat."""
    if not forwarded_uri:
        return None
    try:
        values = parse_qs(urlsplit(forwarded_uri).query).get("token")
    except ValueError:
        return None
    return values[0] if values else None


def resolve_principal(
    verifier: ITokenVerifier,
    authorization: Optional[str],
    forwarded_uri: Optional[str],
) -> Tuple[Optional[Principal], bool]:
    """Devuelve (principal, había_token). El bool distingue 'anónimo' (sin
    token → pasa en modo lenient) de 'token inválido' (401 siempre). El Bearer
    gana sobre `?token=` si vienen ambos."""
    token = extract_bearer_token(authorization) or extract_query_token(forwarded_uri)
    if token is None:
        return None, False
    return verifier.verify(token), True


def identity_headers_for(principal: Optional[Principal]) -> dict:
    """Serializa la identidad al contrato de headers. SIEMPRE devuelve las 5
    claves (vacías si anónimo): Traefik borra-y-copia únicamente los headers que
    el validador emite — omitir uno dejaría pasar el que mandó el cliente
    (spoofing). Si un valor no serializa a latin-1 (requisito de los headers
    HTTP), se degrada a anónimo en vez de tirar un 500."""
    anonymous = {name: "" for name in IDENTITY_HEADERS}
    if principal is None:
        return anonymous
    headers = dict(anonymous)
    try:
        headers[HEADER_USER_ID] = str(principal.user_id) if principal.user_id is not None else ""
        headers[HEADER_USER_EMAIL] = principal.email or ""
        headers[HEADER_USER_ROLE] = principal.role.value if principal.role else ""
        headers[HEADER_SUBSCRIPTION_STATUS] = principal.subscription_status or ""
        headers[HEADER_SUBSCRIPTION_PERIOD_END] = (
            principal.subscription_current_period_end.isoformat()
            if principal.subscription_current_period_end
            else ""
        )
        for value in headers.values():
            value.encode("latin-1")
    except (UnicodeEncodeError, AttributeError):
        return anonymous
    return headers
