import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base
from app.core.database import Base
from app.features.forums.infrastructure.models.social_profile_model import SocialProfileModel
from app.features.forums.infrastructure.repositories.forums_repository import ForumsRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def test_update_profile_aplica_cambios(db_session):
    db_session.add(SocialProfileModel(user_id=1, alias="original", bio="old bio"))
    db_session.commit()
    repo = ForumsRepository(db_session)

    result = repo.update_profile(1, {"bio": "new bio"})

    assert result is not None
    assert result.bio == "new bio"
    assert result.alias == "original"


def test_update_profile_inexistente_retorna_none(db_session):
    repo = ForumsRepository(db_session)

    assert repo.update_profile(404, {"bio": "x"}) is None


def test_update_profile_ignora_user_id_y_cluster_profile(db_session):
    db_session.add(SocialProfileModel(user_id=1, cluster_profile="cluster_a"))
    db_session.commit()
    repo = ForumsRepository(db_session)

    result = repo.update_profile(1, {"user_id": 999, "cluster_profile": "cluster_b"})

    assert result.user_id == 1
    assert result.cluster_profile == "cluster_a"


def test_update_profile_alias_duplicado_lanza_integrity_error(db_session):
    db_session.add(SocialProfileModel(user_id=1, alias="taken"))
    db_session.add(SocialProfileModel(user_id=2, alias="free"))
    db_session.commit()
    repo = ForumsRepository(db_session)

    with pytest.raises(IntegrityError):
        repo.update_profile(2, {"alias": "taken"})
