from salud_prenatal_shared_core.enums import SubscriptionStatusEnum
from app.subscriptions.domain.ports import ISubscriptionRepository
from app.subscriptions.application.dtos import SubscriptionStatusDTO


class GetMySubscriptionUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository):
        self.subscription_repository = subscription_repository

    def execute(self, user_id: int) -> SubscriptionStatusDTO:
        subscription = self.subscription_repository.get_by_user_id(user_id)
        if subscription is None:
            # Sin fila = tratado como pendiente (doctor aun no ha pagado).
            return SubscriptionStatusDTO(status=SubscriptionStatusEnum.pending.value)

        return SubscriptionStatusDTO(
            status=subscription.status.value,
            plan_type=subscription.plan_type.value if subscription.plan_type else None,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
        )
