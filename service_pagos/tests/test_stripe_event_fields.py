"""El adapter debe poblar stripe_event_id/amount en el DTO (base del ledger)."""
from unittest.mock import patch

import stripe

from app.subscriptions.infrastructure.adapters.stripe_gateway_adapter import StripeGatewayAdapter


def _stripe_event(event_type: str, obj: dict, event_id: str = "evt_123"):
    # Event con StripeObjects anidados reales (acceso por atributo, no .get()),
    # que es lo que devuelve construct_event en produccion.
    return stripe.Event.construct_from(
        {"id": event_id, "type": event_type, "data": {"object": obj}}, "sk_test"
    )


@patch("stripe.Webhook.construct_event")
def test_checkout_completed_carries_event_id_and_amount(construct):
    construct.return_value = _stripe_event(
        "checkout.session.completed",
        {
            "client_reference_id": "7",
            "customer": "cus_1",
            "subscription": "sub_1",
            "mode": "subscription",
            "amount_total": 49900,
            "currency": "mxn",
            "metadata": {"user_id": "7", "plan_type": "basic"},
        },
    )

    dto = StripeGatewayAdapter().parse_webhook_event(b"{}", "sig")

    assert dto.kind == "checkout_completed"
    assert dto.stripe_event_id == "evt_123"
    assert dto.amount_cents == 49900
    assert dto.currency == "mxn"


@patch("stripe.Webhook.construct_event")
def test_invoice_paid_carries_amount_paid(construct):
    construct.return_value = _stripe_event(
        "invoice.paid",
        {
            "customer": "cus_1",
            "subscription": "sub_1",
            "amount_paid": 49900,
            "currency": "mxn",
            "lines": {"data": []},
        },
        event_id="evt_inv_1",
    )

    dto = StripeGatewayAdapter().parse_webhook_event(b"{}", "sig")

    assert dto.kind == "payment_succeeded"
    assert dto.stripe_event_id == "evt_inv_1"
    assert dto.amount_cents == 49900


@patch("stripe.Webhook.construct_event")
def test_subscription_deleted_has_event_id_but_no_amount(construct):
    construct.return_value = _stripe_event(
        "customer.subscription.deleted",
        {"customer": "cus_1", "id": "sub_1"},
        event_id="evt_del_1",
    )

    dto = StripeGatewayAdapter().parse_webhook_event(b"{}", "sig")

    assert dto.kind == "subscription_canceled"
    assert dto.stripe_event_id == "evt_del_1"
    assert dto.amount_cents is None
