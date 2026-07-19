import unittest
from unittest.mock import MagicMock
from app.auth.infrastructure.controllers.auth_controller import AuthController


class TestAuthControllerRefresh(unittest.TestCase):
    def test_refresh_delegates_and_returns_use_case_result(self):
        authenticate_uc = MagicMock()
        refresh_uc = MagicMock()
        refresh_uc.execute.return_value = {
            "access_token": "tok", "token_type": "bearer", "subscription_status": "active"
        }
        controller = AuthController(authenticate_uc, refresh_uc)

        result = controller.refresh(email="d@x.com", user_id=1, role="doctor")

        refresh_uc.execute.assert_called_once_with(email="d@x.com", user_id=1, role="doctor")
        self.assertEqual(result["subscription_status"], "active")


if __name__ == "__main__":
    unittest.main()
