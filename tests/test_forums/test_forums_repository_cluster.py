import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base
from app.core.database import Base
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.community_group_entity import CommunityGroupEntity
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.infrastructure.repositories.forums_repository import ForumsRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture()
def repo(db_session):
    return ForumsRepository(db_session)


def test_update_cluster_profile(repo):
    repo.create_profile(SocialProfileEntity(user_id=1, alias="ana"))

    repo.update_cluster_profile(1, "3")

    assert repo.get_profile(1).cluster_profile == "3"


def test_update_cluster_profile_sin_perfil_es_noop(repo):
    repo.update_cluster_profile(999, "3")  # no debe lanzar

    assert repo.get_profile(999) is None


def test_get_feed_by_cluster_solo_autoras_del_cluster(repo):
    repo.create_profile(SocialProfileEntity(user_id=1, alias="a", cluster_profile="3"))
    repo.create_profile(SocialProfileEntity(user_id=2, alias="b", cluster_profile="0"))
    repo.create_post(PostEntity(author_id=1, title="mismo cluster", content="c"))
    repo.create_post(PostEntity(author_id=2, title="otro cluster", content="c"))
    # post de grupo no aparece en el feed (igual que el feed global)
    grupo = repo.create_group(CommunityGroupEntity(name="g", created_by=1))
    repo.create_post(PostEntity(author_id=1, group_id=grupo.group_id, title="en grupo", content="c"))

    posts = repo.get_feed_by_cluster("3")

    assert [p.title for p in posts] == ["mismo cluster"]


def test_get_feed_by_cluster_respeta_limit_offset(repo):
    repo.create_profile(SocialProfileEntity(user_id=1, alias="a", cluster_profile="1"))
    for i in range(3):
        repo.create_post(PostEntity(author_id=1, title=f"p{i}", content="c"))

    assert len(repo.get_feed_by_cluster("1", limit=2, offset=0)) == 2
    assert len(repo.get_feed_by_cluster("1", limit=2, offset=2)) == 1


def test_grupo_con_cluster_tag_y_filtro(repo):
    repo.create_group(CommunityGroupEntity(name="metabolico", created_by=1, cluster_tag="3"))
    repo.create_group(CommunityGroupEntity(name="general", created_by=1))

    grupos = repo.get_groups_by_cluster("3")

    assert [g.name for g in grupos] == ["metabolico"]
    assert grupos[0].cluster_tag == "3"
