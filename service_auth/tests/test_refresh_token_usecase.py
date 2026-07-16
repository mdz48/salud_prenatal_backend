import unittest
from unittest.mock import MagicMock
from jose import jwt
from app.auth.application.refresh_token_usecase import RefreshTokenUseCase
from salud_prenatal_shared_core.jwt_key_provider import get_jwt_key_provider


class TestRefreshTokenUseCase(unittest.TestCase):
    def setUp(self):
        self.auth_read = MagicMock()
        self.usecase = RefreshTokenUseCase(self.auth_read)

    def _decode(self, token):
        p = get_jwt_key_provider()
        return jwt.decode(token, p.get_verification_key(), algorithms=[p.algorithm])

    def test_doctor_gets_fresh_subscription_status_in_token(self):
        self.auth_read.get_subscription_status.return_value = "active"

        result = self.usecase.execute(email="d@x.com", user_id=1, role="doctor")

        self.auth_read.get_subscription_status.assert_called_once_with(1)
        claims = self._decode(result["access_token"])
        self.assertEqual(claims["subscription_status"], "active")
        self.assertEqual(claims["sub"], "d@x.com")
        self.assertEqual(claims["user_id"], 1)
        self.assertEqual(claims["role"], "doctor")
        self.assertEqual(result["subscription_status"], "active")

    def test_non_doctor_never_reads_status(self):
        result = self.usecase.execute(email="p@x.com", user_id=2, role="paciente")

        self.auth_read.get_subscription_status.assert_not_called()
        claims = self._decode(result["access_token"])
        self.assertIsNone(claims["subscription_status"])


if __name__ == "__main__":
    unittest.main()
