"""Idempotencia de webhooks: un evento repetido no debe re-aplicarse.
Regresión directa del bug: cada reintento de one_time_payment_succeeded
sumaba +30 días a current_period_end."""
from unittest.mock import MagicMock

from app.subscriptions.application.handle_payment_event_usecase import HandlePaymentEventUseCase
from app.subscriptions.application.dtos import PaymentEventDTO
from app.subscriptions.domain.subscription_entity import SubscriptionEntity


def _make(event, located_sub):
    gateway = MagicMock()
    gateway.parse_webhook_event.return_value = event
    sub_repo = MagicMock()
    sub_repo.get_by_stripe_subscription_id.return_value = located_sub
    sub_repo.get_by_user_id.return_value = located_sub
    tx_repo = MagicMock()
    tx_repo.exists_by_event_id.return_value = False
    usecase = HandlePaymentEventUseCase(
        subscription_repository=sub_repo,
        payment_gateway=gateway,
        transaction_repository=tx_repo,
    )
    return usecase, sub_repo, tx_repo


def test_duplicate_event_is_skipped_entirely():
    event = PaymentEventDTO(
        kind="one_time_payment_succeeded", user_id=7, stripe_event_id="evt_1"
    )
    usecase, sub_repo, tx_repo = _make(event, SubscriptionEntity(subscription_id=1, user_id=7))
    tx_repo.exists_by_event_id.return_value = True

    usecase.execute(b"{}", "sig")

    sub_repo.update.assert_not_called()
    tx_repo.create.assert_not_called()


def test_processed_event_is_recorded_with_subscription_context():
    event = PaymentEventDTO(
        kind="payment_succeeded",
        stripe_subscription_id="sub_1",
        stripe_event_id="evt_2",
        amount_cents=49900,
        currency="mxn",
    )
    usecase, sub_repo, tx_repo = _make(event, SubscriptionEntity(subscription_id=1, user_id=7))

    usecase.execute(b"{}", "sig")

    sub_repo.update.assert_called_once()
    tx_repo.create.assert_called_once()
    recorded = tx_repo.create.call_args.args[0]
    assert recorded.stripe_event_id == "evt_2"
    assert recorded.user_id == 7
    assert recorded.subscription_id == 1
    assert recorded.kind == "payment_succeeded"
    assert recorded.amount_cents == 49900
    assert recorded.currency == "mxn"


def test_unlocated_event_records_nothing():
    event = PaymentEventDTO(
        kind="payment_succeeded", stripe_subscription_id="sub_x", stripe_event_id="evt_3"
    )
    usecase, sub_repo, tx_repo = _make(event, None)

    usecase.execute(b"{}", "sig")

    sub_repo.update.assert_not_called()
    tx_repo.create.assert_not_called()


def test_irrelevant_event_skips_ledger_lookup():
    usecase, sub_repo, tx_repo = _make(None, None)

    usecase.execute(b"{}", "sig")

    tx_repo.exists_by_event_id.assert_not_called()
    tx_repo.create.assert_not_called()
