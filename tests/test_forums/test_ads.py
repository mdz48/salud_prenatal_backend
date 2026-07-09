import pytest
from unittest.mock import MagicMock

from app.features.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.features.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.ports import IForumsRepository


@pytest.fixture
def mock_forums_repo():
    return MagicMock(spec=IForumsRepository)


def _post(post_id=1, author_id=1, is_ad=False):
    return PostEntity(post_id=post_id, author_id=author_id, title="t", content="c", is_ad=is_ad)


# --- CreatePostUseCase: gating de is_ad ---

def test_post_normal_no_consulta_rol(mock_forums_repo):
    role_lookup = MagicMock()
    mock_forums_repo.create_post.side_effect = lambda p: p
    usecase = CreatePostUseCase(mock_forums_repo, role_lookup)

    usecase.execute(_post(is_ad=False))

    role_lookup.get_role.assert_not_called()


def test_doctor_puede_publicar_ad(mock_forums_repo):
    role_lookup = MagicMock()
    role_lookup.get_role.return_value = "doctor"
    mock_forums_repo.create_post.side_effect = lambda p: p
    usecase = CreatePostUseCase(mock_forums_repo, role_lookup)

    result = usecase.execute(_post(author_id=5, is_ad=True))

    role_lookup.get_role.assert_called_once_with(5)
    assert result.is_ad is True
    mock_forums_repo.create_post.assert_called_once()


def test_no_doctor_no_puede_publicar_ad(mock_forums_repo):
    role_lookup = MagicMock()
    role_lookup.get_role.return_value = "paciente"
    usecase = CreatePostUseCase(mock_forums_repo, role_lookup)

    with pytest.raises(ValueError, match="doctores"):
        usecase.execute(_post(author_id=5, is_ad=True))

    mock_forums_repo.create_post.assert_not_called()


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
