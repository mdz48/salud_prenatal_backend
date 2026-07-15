"""Verifica la auth basada en claims de shared_core (sin DB)."""
import pytest
from fastapi import HTTPException

from salud_prenatal_shared_core.security import create_access_token
from salud_prenatal_shared_core.enums import RoleEnum, SubscriptionStatusEnum
from salud_prenatal_shared_core.auth_dependencies import (
    Principal,
    principal_from_token,
    get_current_user,
    get_current_user_optional,
    require_active_subscription,
    RoleChecker,
)


def _token(**claims):
    return create_access_token(data=claims)


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


class TestGetCurrentUser:
    def test_valid(self):
        token = _token(sub="p@e.com", user_id=3, role="paciente")
        assert get_current_user(token=token).user_id == 3

    def test_invalid_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            get_current_user(token="garbage")
        assert exc.value.status_code == 401

    def test_optional_none_returns_none(self):
        assert get_current_user_optional(token=None) is None

    def test_optional_invalid_returns_none(self):
        assert get_current_user_optional(token="garbage") is None


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
