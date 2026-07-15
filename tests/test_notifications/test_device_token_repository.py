import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DeviceToken.user es un relationship("Usuario") string-based: SQLAlchemy
# configura TODOS los mappers del Base compartido al primer query, así que
# hace falta que el resto de los modelos (Doctor, etc.) ya estén importados
# o la resolución de nombres falla. `main` los importa todos transitivamente.
import main  # noqa: F401

from app.features.notifications.infrastructure.models.device_token_model import DeviceToken
from app.features.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository


@pytest.fixture
def db_session():
    # Motor propio y aislado en memoria: solo crea la tabla device_tokens
    # (sin la de users, que no hace falta para estos tests) para no arrastrar
    # el resto del esquema real.
    engine = create_engine("sqlite:///:memory:")
    DeviceToken.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repo(db_session):
    return DeviceTokenRepository(db_session)


class TestRegisterToken:
    def test_creates_new_token_for_user(self, repo, db_session):
        device = repo.register_token(user_id=1, token="tok-1", device_type="android")

        assert device.id is not None
        assert device.user_id == 1
        assert device.token == "tok-1"
        assert device.device_type == "android"

    def test_creates_new_token_without_user_anonymous(self, repo):
        # Token de dispositivo registrado antes de login (sin sesión).
        device = repo.register_token(user_id=None, token="tok-anon", device_type="android")

        assert device.id is not None
        assert device.user_id is None
        assert device.token == "tok-anon"

    def test_defaults_device_type_to_android(self, repo):
        device = repo.register_token(user_id=1, token="tok-default")
        assert device.device_type == "android"

    def test_reassigns_existing_token_to_new_user(self, repo):
        repo.register_token(user_id=1, token="shared-tok")
        device = repo.register_token(user_id=2, token="shared-tok")

        assert device.user_id == 2
        assert repo.get_tokens_by_user_id(1) == []
        assert repo.get_tokens_by_user_id(2) == ["shared-tok"]

    def test_upgrades_anonymous_token_to_user_on_login(self, repo):
        # Caso central del nuevo diseño: token registrado sin sesión
        # (user_id=None) se reasigna al loguearse, sin duplicar la fila.
        repo.register_token(user_id=None, token="device-tok")
        device = repo.register_token(user_id=42, token="device-tok")

        assert device.user_id == 42
        assert repo.get_all_tokens() == ["device-tok"]

    def test_reassign_does_not_create_duplicate_row(self, repo, db_session):
        repo.register_token(user_id=1, token="tok-x")
        repo.register_token(user_id=2, token="tok-x")

        count = db_session.query(DeviceToken).filter(DeviceToken.token == "tok-x").count()
        assert count == 1

    def test_updates_device_type_on_reassignment(self, repo):
        repo.register_token(user_id=1, token="tok-y", device_type="android")
        device = repo.register_token(user_id=1, token="tok-y", device_type="ios")
        assert device.device_type == "ios"


class TestUnregisterToken:
    def test_removes_matching_user_and_token(self, repo):
        repo.register_token(user_id=1, token="tok-1")
        result = repo.unregister_token(user_id=1, token="tok-1")

        assert result is True
        assert repo.get_tokens_by_user_id(1) == []

    def test_returns_false_when_token_not_found(self, repo):
        result = repo.unregister_token(user_id=1, token="does-not-exist")
        assert result is False

    def test_returns_false_when_token_belongs_to_other_user(self, repo):
        repo.register_token(user_id=1, token="tok-1")
        result = repo.unregister_token(user_id=2, token="tok-1")

        assert result is False
        # No lo borró: sigue asociado al usuario original.
        assert repo.get_tokens_by_user_id(1) == ["tok-1"]


class TestGetTokensByUserId:
    def test_returns_only_tokens_for_that_user(self, repo):
        repo.register_token(user_id=1, token="a")
        repo.register_token(user_id=1, token="b")
        repo.register_token(user_id=2, token="c")

        tokens = repo.get_tokens_by_user_id(1)
        assert sorted(tokens) == ["a", "b"]

    def test_returns_empty_list_for_user_without_tokens(self, repo):
        assert repo.get_tokens_by_user_id(999) == []

    def test_does_not_include_anonymous_tokens(self, repo):
        repo.register_token(user_id=None, token="anon")
        assert repo.get_tokens_by_user_id(1) == []


class TestGetAllTokens:
    def test_returns_empty_when_no_tokens(self, repo):
        assert repo.get_all_tokens() == []

    def test_returns_tokens_across_all_users(self, repo):
        repo.register_token(user_id=1, token="a")
        repo.register_token(user_id=2, token="b")

        assert sorted(repo.get_all_tokens()) == ["a", "b"]

    def test_includes_anonymous_device_level_tokens(self, repo):
        # Recordatorio diario: debe alcanzar dispositivos sin sesión iniciada.
        repo.register_token(user_id=None, token="anon-device")
        repo.register_token(user_id=1, token="logged-in-device")

        assert sorted(repo.get_all_tokens()) == ["anon-device", "logged-in-device"]


class TestDeleteToken:
    def test_deletes_token_regardless_of_owner(self, repo):
        repo.register_token(user_id=1, token="tok-1")
        repo.delete_token("tok-1")

        assert repo.get_all_tokens() == []

    def test_noop_when_token_does_not_exist(self, repo):
        # No debe lanzar excepción.
        repo.delete_token("ghost-token")
        assert repo.get_all_tokens() == []
