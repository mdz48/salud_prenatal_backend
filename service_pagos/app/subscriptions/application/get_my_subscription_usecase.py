from salud_prenatal_shared_core.enums import SubscriptionStatusEnum
from salud_prenatal_shared_core.time import now_cdmx
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

        status_str = subscription.status.value
        now = now_cdmx()
        try:
            is_expired = subscription.current_period_end and subscription.current_period_end < now
        except TypeError:
            now_naive = now.replace(tzinfo=None)
            is_expired = subscription.current_period_end and subscription.current_period_end < now_naive

        if status_str == SubscriptionStatusEnum.active.value and is_expired:
            status_str = "expired"

        return SubscriptionStatusDTO(
            status=status_str,
            plan_type=subscription.plan_type.value if subscription.plan_type else None,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            auto_renewal=subscription.stripe_subscription_id is not None,
        )
