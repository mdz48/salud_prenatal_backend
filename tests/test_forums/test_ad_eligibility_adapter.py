from unittest.mock import MagicMock

from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum
from app.features.forums.infrastructure.adapters.ad_eligibility_adapter import AdEligibilityAdapter
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity


def _sub(plan_type=None, status=SubscriptionStatusEnum.pending):
    return SubscriptionEntity(user_id=1, plan_type=plan_type, status=status)


def test_premium_activo_es_elegible():
    repo = MagicMock()
    repo.get_by_user_id.return_value = _sub(PlanTypeEnum.premium, SubscriptionStatusEnum.active)
    adapter = AdEligibilityAdapter(repo)

    assert adapter.is_premium_active(1) is True


def test_basico_activo_no_es_elegible():
    repo = MagicMock()
    repo.get_by_user_id.return_value = _sub(PlanTypeEnum.basic, SubscriptionStatusEnum.active)
    adapter = AdEligibilityAdapter(repo)

    assert adapter.is_premium_active(1) is False


def test_premium_pendiente_no_es_elegible():
    repo = MagicMock()
    repo.get_by_user_id.return_value = _sub(PlanTypeEnum.premium, SubscriptionStatusEnum.pending)
    adapter = AdEligibilityAdapter(repo)

    assert adapter.is_premium_active(1) is False


def test_premium_vencido_no_es_elegible():
    repo = MagicMock()
    repo.get_by_user_id.return_value = _sub(PlanTypeEnum.premium, SubscriptionStatusEnum.past_due)
    adapter = AdEligibilityAdapter(repo)

    assert adapter.is_premium_active(1) is False


def test_sin_fila_de_suscripcion_no_es_elegible():
    repo = MagicMock()
    repo.get_by_user_id.return_value = None
    adapter = AdEligibilityAdapter(repo)

    assert adapter.is_premium_active(1) is False
