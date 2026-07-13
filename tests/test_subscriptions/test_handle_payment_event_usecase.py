import unittest
from unittest.mock import MagicMock
from datetime import datetime
from app.features.subscriptions.application.handle_payment_event_usecase import HandlePaymentEventUseCase
from app.features.subscriptions.application.dtos import PaymentEventDTO
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum


class TestHandlePaymentEventUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.gateway = MagicMock()
        self.usecase = HandlePaymentEventUseCase(self.repo, self.gateway)

    def _pending_sub(self):
        return SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.pending
        )

    def _updated_entity(self):
        # Devuelve la entidad pasada a repo.update para inspeccionarla.
        return self.repo.update.call_args[0][1]

    def test_ignores_none_event(self):
        self.gateway.parse_webhook_event.return_value = None

        self.usecase.execute(b"payload", "sig")

        self.repo.update.assert_not_called()

    def test_ignores_uncorrelated_event(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="payment_succeeded", user_id=None, stripe_subscription_id="sub_x"
        )
        self.repo.get_by_stripe_subscription_id.return_value = None
        self.repo.get_by_user_id.return_value = None

        self.usecase.execute(b"payload", "sig")

        self.repo.update.assert_not_called()

    def test_checkout_completed_activates_and_stores_ids(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="checkout_completed",
            user_id=1,
            stripe_customer_id="cus_1",
            stripe_subscription_id="sub_1",
            plan_type="basic",
        )
        self.repo.get_by_stripe_subscription_id.return_value = None
        self.repo.get_by_user_id.return_value = self._pending_sub()

        self.usecase.execute(b"payload", "sig")

        updated = self._updated_entity()
        self.assertEqual(updated.status, SubscriptionStatusEnum.active)
        self.assertEqual(updated.stripe_customer_id, "cus_1")
        self.assertEqual(updated.stripe_subscription_id, "sub_1")
        self.assertEqual(updated.plan_type, PlanTypeEnum.basic)

    def test_payment_succeeded_sets_active_and_period_end(self):
        end = datetime(2026, 9, 1)
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="payment_succeeded", stripe_subscription_id="sub_1", current_period_end=end
        )
        self.repo.get_by_stripe_subscription_id.return_value = self._pending_sub()

        self.usecase.execute(b"payload", "sig")

        updated = self._updated_entity()
        self.assertEqual(updated.status, SubscriptionStatusEnum.active)
        self.assertEqual(updated.current_period_end, end)

    def test_payment_failed_sets_past_due(self):
        active = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.active,
            stripe_subscription_id="sub_1",
        )
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="payment_failed", stripe_subscription_id="sub_1"
        )
        self.repo.get_by_stripe_subscription_id.return_value = active

        self.usecase.execute(b"payload", "sig")

        self.assertEqual(self._updated_entity().status, SubscriptionStatusEnum.past_due)

    def test_subscription_canceled_sets_canceled(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="subscription_canceled", stripe_subscription_id="sub_1"
        )
        self.repo.get_by_stripe_subscription_id.return_value = self._pending_sub()

        self.usecase.execute(b"payload", "sig")

        self.assertEqual(self._updated_entity().status, SubscriptionStatusEnum.canceled)

    def test_lookup_falls_back_to_user_id(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="checkout_completed", user_id=1, stripe_subscription_id="sub_1", plan_type="premium"
        )
        self.repo.get_by_stripe_subscription_id.return_value = None
        self.repo.get_by_user_id.return_value = self._pending_sub()

        self.usecase.execute(b"payload", "sig")

        self.repo.get_by_user_id.assert_called_once_with(1)
        self.repo.update.assert_called_once()

    def test_unknown_kind_is_noop(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="some_other_event", stripe_subscription_id="sub_1"
        )
        self.repo.get_by_stripe_subscription_id.return_value = self._pending_sub()

        self.usecase.execute(b"payload", "sig")

        self.repo.update.assert_not_called()

    def test_subscription_updated_syncs_plan_type_from_items(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="subscription_updated",
            stripe_subscription_id="sub_1",
            plan_type_from_items="premium",
        )
        self.repo.get_by_stripe_subscription_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.active,
            stripe_subscription_id="sub_1", plan_type=PlanTypeEnum.basic,
        )

        self.usecase.execute(b"payload", "sig")

        self.assertEqual(self._updated_entity().plan_type, PlanTypeEnum.premium)

    def test_subscription_updated_syncs_cancel_at_period_end(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="subscription_updated",
            stripe_subscription_id="sub_1",
            cancel_at_period_end=True,
        )
        self.repo.get_by_stripe_subscription_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.active,
            stripe_subscription_id="sub_1",
        )

        self.usecase.execute(b"payload", "sig")

        self.assertTrue(self._updated_entity().cancel_at_period_end)

    def test_subscription_canceled_resets_cancel_at_period_end(self):
        self.gateway.parse_webhook_event.return_value = PaymentEventDTO(
            kind="subscription_canceled", stripe_subscription_id="sub_1"
        )
        self.repo.get_by_stripe_subscription_id.return_value = SubscriptionEntity(
            subscription_id=5, user_id=1, status=SubscriptionStatusEnum.active,
            stripe_subscription_id="sub_1", cancel_at_period_end=True,
        )

        self.usecase.execute(b"payload", "sig")

        self.assertFalse(self._updated_entity().cancel_at_period_end)


if __name__ == "__main__":
    unittest.main()

