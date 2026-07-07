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
def repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield ForumsRepository(session)
    session.close()


def test_get_ads_solo_anuncios_globales(repo):
    repo.create_post(PostEntity(author_id=1, title="normal", content="c"))
    repo.create_post(PostEntity(author_id=2, title="anuncio", content="c", is_ad=True))
    # anuncio dentro de un grupo NO cuenta como global
    grupo = repo.create_group(CommunityGroupEntity(name="g", created_by=1))
    repo.create_post(PostEntity(author_id=2, group_id=grupo.group_id, title="ad en grupo", content="c", is_ad=True))

    ads = repo.get_ads()

    assert [a.title for a in ads] == ["anuncio"]
    assert ads[0].is_ad is True


def test_global_feed_excluye_anuncios(repo):
    repo.create_post(PostEntity(author_id=1, title="normal", content="c"))
    repo.create_post(PostEntity(author_id=2, title="anuncio", content="c", is_ad=True))

    feed = repo.get_global_feed()

    assert [p.title for p in feed] == ["normal"]


def test_feed_by_cluster_excluye_anuncios(repo):
    repo.create_profile(SocialProfileEntity(user_id=1, alias="a", cluster_profile="3"))
    repo.create_post(PostEntity(author_id=1, title="normal", content="c"))
    repo.create_post(PostEntity(author_id=1, title="anuncio", content="c", is_ad=True))

    feed = repo.get_feed_by_cluster("3")

    assert [p.title for p in feed] == ["normal"]
