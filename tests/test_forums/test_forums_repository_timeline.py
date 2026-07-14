from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base
from app.core.database import Base
from app.core.time import now_cdmx
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


def test_get_posts_by_author_incluye_grupo_y_ads(repo):
    grupo = repo.create_group(CommunityGroupEntity(name="g", created_by=1))
    repo.create_post(PostEntity(author_id=1, title="normal", content="c"))
    repo.create_post(PostEntity(author_id=1, group_id=grupo.group_id, title="de grupo", content="c"))
    repo.create_post(PostEntity(author_id=1, title="ad", content="c", is_ad=True))
    repo.create_post(PostEntity(author_id=2, title="de otro autor", content="c"))

    posts = repo.get_posts_by_author(1)

    assert {p.title for p in posts} == {"normal", "de grupo", "ad"}


def test_get_posts_by_author_orden_descendente(repo):
    # created_at explicito: server_default=func.now() en SQLite tiene resolucion
    # de 1 segundo, y estos inserts ocurren en el mismo tick de reloj.
    now = now_cdmx()
    repo.create_post(PostEntity(author_id=1, title="primero", content="c", created_at=now - timedelta(seconds=2)))
    repo.create_post(PostEntity(author_id=1, title="segundo", content="c", created_at=now - timedelta(seconds=1)))
    repo.create_post(PostEntity(author_id=1, title="tercero", content="c", created_at=now))

    posts = repo.get_posts_by_author(1)

    assert [p.title for p in posts] == ["tercero", "segundo", "primero"]


def test_get_posts_by_author_respeta_limit_offset(repo):
    for i in range(5):
        repo.create_post(PostEntity(author_id=1, title=f"p{i}", content="c"))

    assert len(repo.get_posts_by_author(1, limit=2, offset=0)) == 2
    assert len(repo.get_posts_by_author(1, limit=2, offset=4)) == 1


def test_get_posts_by_author_sin_posts_devuelve_lista_vacia(repo):
    assert repo.get_posts_by_author(404) == []
