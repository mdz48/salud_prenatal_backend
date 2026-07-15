import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.features.subscriptions.infrastructure.controllers.subscription_controller import SubscriptionController
from app.features.subscriptions.application.dtos import SubscriptionStatusDTO


class TestSubscriptionControllerPortalSession(unittest.TestCase):
    def setUp(self):
        self.create_checkout_uc = MagicMock()
        self.get_my_sub_uc = MagicMock()
        self.handle_event_uc = MagicMock()
        self.create_portal_uc = MagicMock()
        self.controller = SubscriptionController(
            self.create_checkout_uc, self.get_my_sub_uc, self.handle_event_uc, self.create_portal_uc
        )

    def test_create_portal_session_returns_url(self):
        self.create_portal_uc.execute.return_value = "https://billing.stripe.com/p/session/abc"

        result = self.controller.create_portal_session(user_id=1)

        self.assertEqual(result.portal_url, "https://billing.stripe.com/p/session/abc")

    def test_create_portal_session_value_error_returns_400(self):
        self.create_portal_uc.execute.side_effect = ValueError("No active Stripe customer for this user")

        with self.assertRaises(HTTPException) as ctx:
            self.controller.create_portal_session(user_id=1)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_get_my_subscription_includes_cancel_at_period_end(self):
        self.get_my_sub_uc.execute.return_value = SubscriptionStatusDTO(
            status="active", plan_type="premium", cancel_at_period_end=True
        )

        result = self.controller.get_my_subscription(user_id=1)

        self.assertTrue(result.cancel_at_period_end)


if __name__ == "__main__":
    unittest.main()
