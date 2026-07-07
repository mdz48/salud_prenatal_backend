from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum
from app.features.subscriptions.domain.ports import ISubscriptionRepository, IPaymentGateway
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity


class CreateCheckoutSessionUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository, payment_gateway: IPaymentGateway):
        self.subscription_repository = subscription_repository
        self.payment_gateway = payment_gateway

    def execute(self, user_id: int, email: str, plan_type: PlanTypeEnum) -> str:
        # Get-or-create: doctores registrados antes de este feature no tienen fila.
        subscription = self.subscription_repository.get_by_user_id(user_id)
        if subscription is None:
            self.subscription_repository.create(
                SubscriptionEntity(user_id=user_id, status=SubscriptionStatusEnum.pending)
            )

        result = self.payment_gateway.create_checkout_session(user_id, email, plan_type)
        return result.checkout_url
