import unittest
from unittest.mock import MagicMock
from datetime import datetime
from app.features.subscriptions.application.get_my_subscription_usecase import GetMySubscriptionUseCase
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum


class TestGetMySubscriptionUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.usecase = GetMySubscriptionUseCase(self.repo)

    def test_returns_status_when_subscription_exists(self):
        end = datetime(2026, 8, 1)
        self.repo.get_by_user_id.return_value = SubscriptionEntity(
            subscription_id=5,
            user_id=1,
            plan_type=PlanTypeEnum.premium,
            status=SubscriptionStatusEnum.active,
            current_period_end=end,
        )

        result = self.usecase.execute(user_id=1)

        self.assertEqual(result.status, "active")
        self.assertEqual(result.plan_type, "premium")
        self.assertEqual(result.current_period_end, end)

    def test_returns_pending_when_missing(self):
        self.repo.get_by_user_id.return_value = None

        result = self.usecase.execute(user_id=99)

        self.assertEqual(result.status, "pending")
        self.assertIsNone(result.plan_type)
        self.assertIsNone(result.current_period_end)


if __name__ == "__main__":
    unittest.main()
