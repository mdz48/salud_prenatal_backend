from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum
from app.features.forums.domain.ports import IAdEligibilityLookup
from app.features.subscriptions.domain.ports import ISubscriptionRepository

class AdEligibilityAdapter(IAdEligibilityLookup):
    """Resuelve si un autor puede publicar anuncios (forums -> subscriptions):
    solo con plan premium y suscripcion activa. Un doctor legacy sin fila de
    suscripcion, o con plan basico/estado inactivo, no es elegible."""

    def __init__(self, subscription_repository: ISubscriptionRepository):
        self.subscription_repository = subscription_repository

    def is_premium_active(self, user_id: int) -> bool:
        subscription = self.subscription_repository.get_by_user_id(user_id)
        if not subscription:
            return False
        return (
            subscription.plan_type == PlanTypeEnum.premium
            and subscription.status == SubscriptionStatusEnum.active
        )
