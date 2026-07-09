from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.features.users.domain.user_entity import UserEntity

from dependency_injector.wiring import Provide, inject
from app.core.containers import Container
from app.core.enums import RoleEnum, SubscriptionStatusEnum
from app.features.users.domain.ports import IUserRepository
from app.features.subscriptions.domain.ports import ISubscriptionRepository
from app.core.security import get_secret_key, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def authenticate_token(token: str, user_repo: IUserRepository) -> UserEntity | None:
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
    except JWTError:
        return None
    return user_repo.get_by_email(email)


@inject
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(Provide[Container.user_repository])
) -> UserEntity:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = authenticate_token(token, user_repo)
    if user is None:
        raise credentials_exception
    return user

@inject
def require_active_subscription(
    current_user: UserEntity = Depends(get_current_user),
    subscription_repo: ISubscriptionRepository = Depends(Provide[Container.subscription_repository]),
) -> UserEntity:
    """Exige suscripcion activa a los doctores. Otros roles pasan sin verificar
    (solo los doctores pagan). Sin fila o status != active -> HTTP 402."""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str != RoleEnum.doctor.value:
        return current_user

    subscription = subscription_repo.get_by_user_id(current_user.user_id)
    current_status = subscription.status.value if subscription else "none"
    if current_status != SubscriptionStatusEnum.active.value:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Active subscription required. Current status: {current_status}",
        )
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserEntity = Depends(get_current_user)):
        user_role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        allowed_strs = [r.value if hasattr(r, 'value') else str(r) for r in self.allowed_roles]
        if user_role_str not in allowed_strs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role"
            )
        return current_user
