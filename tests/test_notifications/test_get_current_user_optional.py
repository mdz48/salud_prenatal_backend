from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_user_optional
from app.core.security import create_access_token


class TestGetCurrentUserOptional:
    def test_returns_none_when_no_token(self):
        result = get_current_user_optional(token=None, user_repo=MagicMock())
        assert result is None

    def test_returns_none_for_malformed_token(self):
        result = get_current_user_optional(token="not-a-real-jwt", user_repo=MagicMock())
        assert result is None

    def test_returns_none_for_token_signed_with_wrong_key(self):
        from jose import jwt as jose_jwt

        bogus_token = jose_jwt.encode({"sub": "a@b.com"}, "wrong-key", algorithm="HS256")
        result = get_current_user_optional(token=bogus_token, user_repo=MagicMock())
        assert result is None

    def test_returns_user_for_valid_token(self):
        token = create_access_token({"sub": "patient@example.com"})
        fake_user = MagicMock(user_id=7, email="patient@example.com")
        user_repo = MagicMock()
        user_repo.get_by_email.return_value = fake_user

        result = get_current_user_optional(token=token, user_repo=user_repo)

        assert result is fake_user
        user_repo.get_by_email.assert_called_once_with("patient@example.com")

    def test_returns_none_when_user_not_found_in_db(self):
        # Token válido pero el usuario ya no existe (cuenta borrada, etc).
        token = create_access_token({"sub": "ghost@example.com"})
        user_repo = MagicMock()
        user_repo.get_by_email.return_value = None

        result = get_current_user_optional(token=token, user_repo=user_repo)

        assert result is None

    def test_returns_none_when_token_has_no_subject_claim(self):
        token = create_access_token({"foo": "bar"})
        result = get_current_user_optional(token=token, user_repo=MagicMock())
        assert result is None

    def test_never_raises_httpexception(self):
        # A diferencia de get_current_user, esta variante nunca debe
        # propagar un 401: el endpoint debe seguir funcionando sin sesión.
        try:
            get_current_user_optional(token="garbage", user_repo=MagicMock())
        except HTTPException:
            pytest.fail("get_current_user_optional no debería lanzar HTTPException")
