from datetime import timedelta

import pytest
from unittest.mock import MagicMock

from app.features.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.features.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.features.forums.domain.exceptions import AdPermissionError, AdRateLimitError
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.ports import IForumsRepository
from app.core.time import now_cdmx


@pytest.fixture
def mock_forums_repo():
    repo = MagicMock(spec=IForumsRepository)
    repo.count_ads_by_author_since.return_value = 0
    return repo


def _post(post_id=1, author_id=1, is_ad=False):
    return PostEntity(post_id=post_id, author_id=author_id, title="t", content="c", is_ad=is_ad)


# --- CreatePostUseCase: gating de is_ad por suscripcion premium activa ---

def test_post_normal_no_consulta_elegibilidad_ni_cuenta(mock_forums_repo):
    ad_eligibility = MagicMock()
    mock_forums_repo.create_post.side_effect = lambda p: p
    usecase = CreatePostUseCase(mock_forums_repo, ad_eligibility)

    usecase.execute(_post(is_ad=False))

    ad_eligibility.is_premium_active.assert_not_called()
    mock_forums_repo.count_ads_by_author_since.assert_not_called()


def test_premium_activo_bajo_tope_puede_publicar_ad(mock_forums_repo):
    ad_eligibility = MagicMock()
    ad_eligibility.is_premium_active.return_value = True
    mock_forums_repo.count_ads_by_author_since.return_value = 9
    mock_forums_repo.create_post.side_effect = lambda p: p
    usecase = CreatePostUseCase(mock_forums_repo, ad_eligibility)

    result = usecase.execute(_post(author_id=5, is_ad=True))

    ad_eligibility.is_premium_active.assert_called_once_with(5)
    assert result.is_ad is True
    mock_forums_repo.create_post.assert_called_once()


def test_sin_premium_activo_no_puede_publicar_ad(mock_forums_repo):
    ad_eligibility = MagicMock()
    ad_eligibility.is_premium_active.return_value = False
    usecase = CreatePostUseCase(mock_forums_repo, ad_eligibility)

    with pytest.raises(AdPermissionError, match="premium"):
        usecase.execute(_post(author_id=5, is_ad=True))

    mock_forums_repo.create_post.assert_not_called()


def test_supera_tope_semanal_no_puede_publicar_ad(mock_forums_repo):
    ad_eligibility = MagicMock()
    ad_eligibility.is_premium_active.return_value = True
    mock_forums_repo.count_ads_by_author_since.return_value = 10
    usecase = CreatePostUseCase(mock_forums_repo, ad_eligibility)

    with pytest.raises(AdRateLimitError, match="semanal"):
        usecase.execute(_post(author_id=5, is_ad=True))

    mock_forums_repo.create_post.assert_not_called()


def test_conteo_semanal_usa_ventana_de_7_dias(mock_forums_repo):
    ad_eligibility = MagicMock()
    ad_eligibility.is_premium_active.return_value = True
    mock_forums_repo.create_post.side_effect = lambda p: p
    usecase = CreatePostUseCase(mock_forums_repo, ad_eligibility)

    usecase.execute(_post(author_id=5, is_ad=True))

    args, _ = mock_forums_repo.count_ads_by_author_since.call_args
    author_id, since = args
    assert author_id == 5
    assert abs((now_cdmx() - since) - timedelta(days=7)) < timedelta(seconds=5)


# --- GetRecommendedFeedUseCase: intercala anuncios ---

def test_feed_recomendado_intercala_ads(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile="3")
    normales = [_post(i) for i in range(1, 5)]  # 4 posts
    mock_forums_repo.get_feed_by_cluster.return_value = normales
    mock_forums_repo.get_ads.return_value = [_post(99, author_id=7, is_ad=True)]
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    # el ad queda tras los 4 posts normales (every=4)
    assert [p.post_id for p in result] == [1, 2, 3, 4, 99]
    assert result[-1].is_ad is True


def test_feed_recomendado_sin_ads_queda_igual(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = None
    mock_forums_repo.get_global_feed.return_value = [_post(1), _post(2)]
    mock_forums_repo.get_ads.return_value = []
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    assert [p.post_id for p in result] == [1, 2]
