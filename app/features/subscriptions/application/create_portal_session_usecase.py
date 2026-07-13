from app.features.subscriptions.domain.ports import ISubscriptionRepository, IPaymentGateway


class CreatePortalSessionUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository, payment_gateway: IPaymentGateway):
        self.subscription_repository = subscription_repository
        self.payment_gateway = payment_gateway

    def execute(self, user_id: int) -> str:
        sub = self.subscription_repository.get_by_user_id(user_id)
        if sub is None or sub.stripe_customer_id is None:
            raise ValueError("No active Stripe customer for this user")
        return self.payment_gateway.create_portal_session(sub.stripe_customer_id)
