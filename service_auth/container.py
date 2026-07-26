"""Composition root del servicio auth — slice mínimo: leer credenciales + emitir JWT."""
from dependency_injector import containers, providers

from salud_prenatal_shared_core.database import get_session_factory

from app.auth.infrastructure.repositories.auth_repository import AuthReadRepository
from app.auth.application.authenticate_user_usecase import AuthenticateUserUseCase
from app.auth.application.refresh_token_usecase import RefreshTokenUseCase
from app.auth.infrastructure.controllers.auth_controller import AuthController


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.auth.infrastructure.routes.auth_router",
        ]
    )

    db = providers.ContextLocalSingleton(lambda: get_session_factory()())

    auth_read_repository = providers.Factory(AuthReadRepository, db=db)

    authenticate_user_use_case = providers.Factory(
        AuthenticateUserUseCase, auth_read=auth_read_repository
    )

    refresh_token_use_case = providers.Factory(
        RefreshTokenUseCase, auth_read=auth_read_repository
    )

    auth_controller = providers.Factory(
        AuthController,
        authenticate_user_use_case=authenticate_user_use_case,
        refresh_token_use_case=refresh_token_use_case,
    )
