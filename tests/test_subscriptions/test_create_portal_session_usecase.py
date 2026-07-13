import unittest
from unittest.mock import MagicMock
from app.features.subscriptions.application.create_portal_session_usecase import CreatePortalSessionUseCase
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity


class TestCreatePortalSessionUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.gateway = MagicMock()
        self.usecase = CreatePortalSessionUseCase(self.repo, self.gateway)

    def test_returns_portal_url_when_customer_exists(self):
        self.repo.get_by_user_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, stripe_customer_id="cus_1"
        )
        self.gateway.create_portal_session.return_value = "https://billing.stripe.com/p/session/abc"

        url = self.usecase.execute(user_id=1)

        self.assertEqual(url, "https://billing.stripe.com/p/session/abc")
        self.gateway.create_portal_session.assert_called_once_with("cus_1")

    def test_raises_when_subscription_missing(self):
        self.repo.get_by_user_id.return_value = None

        with self.assertRaises(ValueError):
            self.usecase.execute(user_id=1)

    def test_raises_when_stripe_customer_id_is_none(self):
        self.repo.get_by_user_id.return_value = SubscriptionEntity(user_id=1, stripe_customer_id=None)

        with self.assertRaises(ValueError):
            self.usecase.execute(user_id=1)


if __name__ == "__main__":
    unittest.main()
