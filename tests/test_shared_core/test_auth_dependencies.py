"""Verifica la auth basada en headers de identidad (X-User-*) de shared_core.

Modelo de confianza: Traefik ForwardAuth valida el JWT UNA vez en el edge
(gateway /validate) e inyecta los headers; los servicios solo los leen.
principal_from_token se conserva porque lo usa el validador del gateway.
"""
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from salud_prenatal_shared_core.security import create_access_token
from salud_prenatal_shared_core.enums import RoleEnum, SubscriptionStatusEnum
from salud_prenatal_shared_core.auth_dependencies import (
    Principal,
    principal_from_token,
    principal_from_headers,
    get_current_user,
    get_current_user_optional,
    require_active_subscription,
    RoleChecker,
    HEADER_USER_ID,
    HEADER_USER_EMAIL,
    HEADER_USER_ROLE,
    HEADER_SUBSCRIPTION_STATUS,
    HEADER_SUBSCRIPTION_PERIOD_END,
    IDENTITY_HEADERS,
)


def _token(**claims):
    return create_access_token(data=claims)


def _request(headers: dict) -> Request:
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
    }
    return Request(scope)


class TestPrincipalFromToken:
    def test_valid_token_builds_principal(self):
        token = _token(sub="doc@example.com", user_id=7, role="doctor",
                       subscription_status="active")
        p = principal_from_token(token)
        assert p == Principal(user_id=7, email="doc@example.com",
                              role=RoleEnum.doctor, subscription_status="active")
        assert p.role is RoleEnum.doctor  # se parsea a enum

    def test_invalid_token_returns_none(self):
        assert principal_from_token("no-es-un-jwt") is None

    def test_token_without_sub_returns_none(self):
        assert principal_from_token(_token(user_id=1, role="doctor")) is None

    def test_unknown_role_stays_none(self):
        p = principal_from_token(_token(sub="x@e.com", role="marciano"))
        assert p is not None and p.role is None


class TestPrincipalFromHeaders:
    def test_full_headers_build_principal(self):
        p = principal_from_headers({
            HEADER_USER_ID: "7",
            HEADER_USER_EMAIL: "doc@example.com",
            HEADER_USER_ROLE: "doctor",
            HEADER_SUBSCRIPTION_STATUS: "active",
            HEADER_SUBSCRIPTION_PERIOD_END: "2026-08-15T12:00:00",
        })
        assert p.user_id == 7
        assert p.email == "doc@example.com"
        assert p.role is RoleEnum.doctor
        assert p.subscription_status == "active"
        assert p.subscription_current_period_end.year == 2026

    def test_lookup_is_case_insensitive(self):
        p = principal_from_headers({"x-user-email": "d@e.com", "X-USER-ID": "1"})
        assert p is not None and p.user_id == 1 and p.email == "d@e.com"

    def test_empty_email_is_anonymous(self):
        # Header vacío == ausente: mismo criterio de presencia que el claim `sub`.
        assert principal_from_headers({HEADER_USER_EMAIL: "", HEADER_USER_ID: "7"}) is None

    def test_missing_email_is_anonymous(self):
        assert principal_from_headers({HEADER_USER_ID: "7"}) is None

    def test_all_empty_is_anonymous(self):
        assert principal_from_headers({h: "" for h in IDENTITY_HEADERS}) is None

    def test_unknown_role_stays_none(self):
        p = principal_from_headers({HEADER_USER_EMAIL: "x@e.com", HEADER_USER_ROLE: "marciano"})
        assert p is not None and p.role is None

    def test_non_numeric_user_id_degrades_to_none(self):
        p = principal_from_headers({HEADER_USER_EMAIL: "x@e.com", HEADER_USER_ID: "abc"})
        assert p is not None and p.user_id is None

    def test_malformed_period_end_degrades_to_none(self):
        p = principal_from_headers({HEADER_USER_EMAIL: "x@e.com",
                                    HEADER_SUBSCRIPTION_PERIOD_END: "no-es-fecha"})
        assert p is not None and p.subscription_current_period_end is None

    def test_starlette_headers_supported(self):
        req = _request({HEADER_USER_EMAIL: "d@e.com", HEADER_USER_ID: "3"})
        p = principal_from_headers(req.headers)
        assert p is not None and p.user_id == 3


class TestGetCurrentUser:
    def test_request_with_identity_headers_builds_principal(self):
        req = _request({HEADER_USER_ID: "3", HEADER_USER_EMAIL: "p@e.com",
                        HEADER_USER_ROLE: "paciente"})
        principal = get_current_user_optional(request=req, _token=None)
        assert principal is not None and principal.user_id == 3
        assert get_current_user(principal=principal).user_id == 3

    def test_anonymous_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            get_current_user(principal=None)
        assert exc.value.status_code == 401
        assert exc.value.headers["WWW-Authenticate"] == "Bearer"

    def test_optional_without_headers_returns_none(self):
        assert get_current_user_optional(request=_request({}), _token=None) is None

    def test_optional_with_empty_headers_returns_none(self):
        req = _request({HEADER_USER_ID: "", HEADER_USER_EMAIL: ""})
        assert get_current_user_optional(request=req, _token=None) is None


class TestRequireActiveSubscription:
    def test_doctor_active_passes(self):
        p = Principal(user_id=1, email="d@e.com", role=RoleEnum.doctor,
                      subscription_status=SubscriptionStatusEnum.active.value)
        assert require_active_subscription(current_user=p) is p

    def test_doctor_without_active_raises_402(self):
        p = Principal(user_id=1, email="d@e.com", role=RoleEnum.doctor,
                      subscription_status="pending")
        with pytest.raises(HTTPException) as exc:
            require_active_subscription(current_user=p)
        assert exc.value.status_code == 402

    def test_doctor_missing_status_raises_402(self):
        p = Principal(user_id=1, email="d@e.com", role=RoleEnum.doctor,
                      subscription_status=None)
        with pytest.raises(HTTPException) as exc:
            require_active_subscription(current_user=p)
        assert exc.value.status_code == 402

    def test_non_doctor_passes_regardless(self):
        p = Principal(user_id=2, email="p@e.com", role=RoleEnum.patient,
                      subscription_status=None)
        assert require_active_subscription(current_user=p) is p


class TestRoleChecker:
    def test_allowed_role_passes(self):
        checker = RoleChecker([RoleEnum.doctor])
        p = Principal(user_id=1, email="d@e.com", role=RoleEnum.doctor)
        assert checker(current_user=p) is p

    def test_disallowed_role_raises_403(self):
        checker = RoleChecker([RoleEnum.doctor])
        p = Principal(user_id=2, email="p@e.com", role=RoleEnum.patient)
        with pytest.raises(HTTPException) as exc:
            checker(current_user=p)
        assert exc.value.status_code == 403
