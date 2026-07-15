"""Read-model de solo lectura sobre `subscriptions` (owned por el servicio pagos).

Transaccional lo lee SOLO para la elegibilidad de anuncios en foros, que exige
`plan_type == premium` y `status == active`. Como el claim del JWT únicamente trae
`subscription_status` (no el plan), la elegibilidad se resuelve por lectura directa
a la tabla, no por claim.
"""
from sqlalchemy import Column, Integer, Enum as SAEnum

from salud_prenatal_shared_core.database import ReadModelBase as Base
from salud_prenatal_shared_core.enums import PlanTypeEnum, SubscriptionStatusEnum


class SubscriptionRead(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"extend_existing": True}

    subscription_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    plan_type = Column(SAEnum(PlanTypeEnum), nullable=True)
    status = Column(SAEnum(SubscriptionStatusEnum), nullable=False)
