import unittest
from unittest.mock import patch
import stripe
from app.features.subscriptions.infrastructure.adapters.stripe_gateway_adapter import StripeGatewayAdapter


def _stripe_event(event_type: str, obj: dict):
    # Construye un Event de Stripe con StripeObjects anidados reales (no dicts),
    # que es lo que devuelve construct_event en produccion.
    return stripe.Event.construct_from(
        {"type": event_type, "data": {"object": obj}}, "sk_test"
    )


class TestStripeGatewayAdapterWebhookParsing(unittest.TestCase):
    """Regresion: los StripeObject usan acceso por atributo, no .get(). El parser
    debe extraer campos anidados (metadata) sin romperse."""

    def setUp(self):
        self.adapter = StripeGatewayAdapter()

    @patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_x"})
    @patch("stripe.Webhook.construct_event")
    def test_checkout_completed_maps_nested_metadata(self, construct):
        construct.return_value = _stripe_event(
            "checkout.session.completed",
            {
                "client_reference_id": "7",
                "customer": "cus_1",
                "subscription": "sub_1",
                "metadata": {"user_id": "7", "plan_type": "basic"},
            },
        )

        dto = self.adapter.parse_webhook_event(b"{}", "sig")

        self.assertEqual(dto.kind, "checkout_completed")
        self.assertEqual(dto.user_id, 7)
        self.assertEqual(dto.stripe_customer_id, "cus_1")
        self.assertEqual(dto.stripe_subscription_id, "sub_1")
        self.assertEqual(dto.plan_type, "basic")

    @patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_x"})
    @patch("stripe.Webhook.construct_event")
    def test_subscription_deleted_maps_to_canceled(self, construct):
        construct.return_value = _stripe_event(
            "customer.subscription.deleted", {"id": "sub_1", "customer": "cus_1"}
        )

        dto = self.adapter.parse_webhook_event(b"{}", "sig")

        self.assertEqual(dto.kind, "subscription_canceled")
        self.assertEqual(dto.stripe_subscription_id, "sub_1")

    @patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_x"})
    @patch("stripe.Webhook.construct_event")
    def test_irrelevant_event_returns_none(self, construct):
        construct.return_value = _stripe_event("customer.created", {"id": "cus_1"})

        self.assertIsNone(self.adapter.parse_webhook_event(b"{}", "sig"))


class TestStripeGatewayAdapterPortalSession(unittest.TestCase):
    def setUp(self):
        self.adapter = StripeGatewayAdapter()

    @patch.dict("os.environ", {
        "STRIPE_PRIVATE_KEY": "sk_test_x",
        "FRONTEND_URL": "saludprenatal://payment-callback",
    })
    @patch("stripe.billing_portal.Session.create")
    def test_create_portal_session_returns_url(self, create_mock):
        create_mock.return_value = stripe.billing_portal.Session.construct_from(
            {"id": "bps_1", "url": "https://billing.stripe.com/p/session/abc"}, "sk_test"
        )

        url = self.adapter.create_portal_session("cus_1")

        self.assertEqual(url, "https://billing.stripe.com/p/session/abc")
        create_mock.assert_called_once_with(
            customer="cus_1",
            return_url="saludprenatal://payment-callback/subscription/me",
        )


if __name__ == "__main__":
    unittest.main()
