import unittest
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity


class TestSubscriptionEntity(unittest.TestCase):
    def test_cancel_at_period_end_defaults_false(self):
        sub = SubscriptionEntity(user_id=1)
        self.assertFalse(sub.cancel_at_period_end)

    def test_cancel_at_period_end_can_be_set_true(self):
        sub = SubscriptionEntity(user_id=1, cancel_at_period_end=True)
        self.assertTrue(sub.cancel_at_period_end)


if __name__ == "__main__":
    unittest.main()
