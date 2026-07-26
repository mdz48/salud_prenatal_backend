"""IAdEligibilityLookup leyendo `subscriptions` directo de la DB compartida
(read-model). Elegible = plan premium + estado activo. El claim del JWT no basta
(no trae plan_type), por eso se lee la tabla."""
from sqlalchemy.orm import Session

from salud_prenatal_shared_core.enums import PlanTypeEnum, SubscriptionStatusEnum
from app.forums.domain.ports import IAdEligibilityLookup
from app.readmodels.subscriptions_readmodels import SubscriptionRead


class AdEligibilityAdapter(IAdEligibilityLookup):
    def __init__(self, db: Session):
        self.db = db

    def is_premium_active(self, user_id: int) -> bool:
        sub = self.db.query(SubscriptionRead).filter(SubscriptionRead.user_id == user_id).first()
        if not sub:
            return False
        return sub.plan_type == PlanTypeEnum.premium and sub.status == SubscriptionStatusEnum.active
