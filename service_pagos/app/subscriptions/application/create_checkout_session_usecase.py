from typing import Dict
from salud_prenatal_shared_core.enums import PlanTypeEnum, SubscriptionStatusEnum, PaymentModeEnum
from app.subscriptions.domain.ports import ISubscriptionRepository, ICheckoutStrategy
from app.subscriptions.domain.subscription_entity import SubscriptionEntity


class CreateCheckoutSessionUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository, checkout_strategies: Dict[PaymentModeEnum, ICheckoutStrategy]):
        self.subscription_repository = subscription_repository
        self.checkout_strategies = checkout_strategies

    def execute(self, user_id: int, email: str, plan_type: PlanTypeEnum, payment_mode: PaymentModeEnum = PaymentModeEnum.recurring) -> str:
        # Get-or-create: doctores registrados antes de este feature no tienen fila.
        subscription = self.subscription_repository.get_by_user_id(user_id)
        if subscription is None:
            subscription = self.subscription_repository.create(
                SubscriptionEntity(user_id=user_id, status=SubscriptionStatusEnum.pending)
            )

        strategy = self.checkout_strategies.get(payment_mode)
        if strategy is None:
            raise ValueError(f"Unsupported payment mode: {payment_mode}")
        
        result = strategy.create_checkout_session(
            user_id=user_id, 
            email=email, 
            plan_type=plan_type, 
            stripe_customer_id=subscription.stripe_customer_id if subscription else None
        )
        # Si la estrategia creó el customer, lo actualizamos en DB
        if result.stripe_customer_id and (not subscription or subscription.stripe_customer_id != result.stripe_customer_id):
            if subscription:
                subscription.stripe_customer_id = result.stripe_customer_id
                self.subscription_repository.update(subscription.subscription_id, subscription)
                
        return result.checkout_url
