import pytest
from unittest.mock import MagicMock

from app.features.forums.application.profiles.create_profile_usecase import CreateProfileUseCase
from app.features.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.features.forums.application.groups.get_recommended_groups_usecase import GetRecommendedGroupsUseCase
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.community_group_entity import CommunityGroupEntity
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.ports import IForumsRepository


@pytest.fixture
def mock_forums_repo():
    return MagicMock(spec=IForumsRepository)


def _post(post_id=1, author_id=1):
    return PostEntity(post_id=post_id, author_id=author_id, title="t", content="c")


def _group(group_id=1, cluster_tag=None):
    return CommunityGroupEntity(group_id=group_id, name="g", created_by=1, cluster_tag=cluster_tag)


# --- CreateProfileUseCase: cluster derivado del ML, nunca del cliente ---

def test_create_profile_resuelve_cluster_del_lookup(mock_forums_repo):
    lookup = MagicMock()
    lookup.get_cluster_by_user_id.return_value = "3"
    mock_forums_repo.create_profile.side_effect = lambda p: p
    usecase = CreateProfileUseCase(mock_forums_repo, lookup)

    result = usecase.execute(SocialProfileEntity(user_id=1, alias="a"))

    lookup.get_cluster_by_user_id.assert_called_once_with(1)
    assert result.cluster_profile == "3"


def test_create_profile_sin_prediccion_deja_cluster_none(mock_forums_repo):
    lookup = MagicMock()
    lookup.get_cluster_by_user_id.return_value = None
    mock_forums_repo.create_profile.side_effect = lambda p: p
    usecase = CreateProfileUseCase(mock_forums_repo, lookup)

    result = usecase.execute(SocialProfileEntity(user_id=1, alias="a", cluster_profile="9"))

    # el valor que venga del request se ignora: solo el ML lo determina
    assert result.cluster_profile is None


# --- GetRecommendedFeedUseCase ---

def test_feed_recomendado_filtra_por_cluster(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile="3")
    mock_forums_repo.get_feed_by_cluster.return_value = [_post(1), _post(2)]
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    mock_forums_repo.get_feed_by_cluster.assert_called_once_with("3", 10, 0)
    assert len(result) == 2


def test_feed_recomendado_sin_cluster_fallback_global(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile=None)
    mock_forums_repo.get_global_feed.return_value = [_post(9)]
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    mock_forums_repo.get_feed_by_cluster.assert_not_called()
    mock_forums_repo.get_global_feed.assert_called_once_with(10, 0)
    assert result[0].post_id == 9


def test_feed_recomendado_sin_perfil_fallback_global(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = None
    mock_forums_repo.get_global_feed.return_value = []
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    mock_forums_repo.get_global_feed.assert_called_once_with(10, 0)
    assert result == []


def test_feed_recomendado_cluster_vacio_fallback_global(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile="0")
    mock_forums_repo.get_feed_by_cluster.return_value = []
    mock_forums_repo.get_global_feed.return_value = [_post(5)]
    usecase = GetRecommendedFeedUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1, limit=10, offset=0)

    assert result[0].post_id == 5


# --- GetRecommendedGroupsUseCase ---

def test_grupos_recomendados_filtra_por_cluster(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile="3")
    mock_forums_repo.get_groups_by_cluster.return_value = [_group(1, "3")]
    usecase = GetRecommendedGroupsUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1)

    mock_forums_repo.get_groups_by_cluster.assert_called_once_with("3")
    assert result[0].group_id == 1


def test_grupos_recomendados_sin_cluster_fallback_todos(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = None
    mock_forums_repo.get_groups.return_value = [_group(2)]
    usecase = GetRecommendedGroupsUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1)

    mock_forums_repo.get_groups_by_cluster.assert_not_called()
    assert result[0].group_id == 2


def test_grupos_recomendados_sin_resultados_fallback_todos(mock_forums_repo):
    mock_forums_repo.get_profile.return_value = SocialProfileEntity(user_id=1, cluster_profile="1")
    mock_forums_repo.get_groups_by_cluster.return_value = []
    mock_forums_repo.get_groups.return_value = [_group(3)]
    usecase = GetRecommendedGroupsUseCase(mock_forums_repo)

    result = usecase.execute(user_id=1)

    assert result[0].group_id == 3
