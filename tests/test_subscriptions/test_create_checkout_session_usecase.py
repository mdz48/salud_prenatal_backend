import unittest
from unittest.mock import MagicMock
from app.features.subscriptions.application.create_checkout_session_usecase import CreateCheckoutSessionUseCase
from app.features.subscriptions.application.dtos import CheckoutSessionResult
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum


class TestCreateCheckoutSessionUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.gateway = MagicMock()
        self.gateway.create_checkout_session.return_value = CheckoutSessionResult(
            checkout_url="https://checkout.stripe.com/session_abc"
        )
        self.usecase = CreateCheckoutSessionUseCase(self.repo, self.gateway)

    def test_returns_checkout_url(self):
        self.repo.get_by_user_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.pending
        )

        url = self.usecase.execute(user_id=1, email="doc@x.com", plan_type=PlanTypeEnum.basic)

        self.assertEqual(url, "https://checkout.stripe.com/session_abc")
        self.gateway.create_checkout_session.assert_called_once_with(1, "doc@x.com", PlanTypeEnum.basic)

    def test_creates_pending_row_when_none_exists(self):
        self.repo.get_by_user_id.return_value = None

        self.usecase.execute(user_id=7, email="new@x.com", plan_type=PlanTypeEnum.premium)

        self.repo.create.assert_called_once()
        created = self.repo.create.call_args[0][0]
        self.assertEqual(created.user_id, 7)
        self.assertEqual(created.status, SubscriptionStatusEnum.pending)

    def test_does_not_create_when_row_exists(self):
        self.repo.get_by_user_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.pending
        )

        self.usecase.execute(user_id=1, email="doc@x.com", plan_type=PlanTypeEnum.basic)

        self.repo.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
