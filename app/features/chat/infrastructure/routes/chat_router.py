from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.core.dependencies import get_current_user, authenticate_token
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.ports import IUserRepository
from fastapi import APIRouter, WebSocket, WebSocketException, Depends, Query, status
from app.features.chat.infrastructure.controllers.chat_controller import ChatController
from app.features.chat.infrastructure.schemas.chat_schema import MessageResponse
from app.features.chat.domain.inbox_item_response import InboxItemResponse
from app.features.chat.domain.dtos import ChatUser
from typing import List

router= APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/inbox", response_model=List[InboxItemResponse])
@inject
def get_inbox(
    current_user: UserEntity = Depends(get_current_user),
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    return controller.get_inbox(current_user.user_id)

@router.get("/contacts", response_model=List[ChatUser])
@inject
def get_contacts(
    current_user: UserEntity = Depends(get_current_user),
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return controller.get_contacts(current_user.user_id, role)

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
@inject
def get_chat_history(
    other_user_id: int,
    current_user: UserEntity = Depends(get_current_user),
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    return controller.get_chat_history(current_user.user_id, other_user_id)

@router.websocket("/ws")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    controller: ChatController = Depends(Provide[Container.chat_controller]),
    user_repo: IUserRepository = Depends(Provide[Container.user_repository]),
):
    user = authenticate_token(token, user_repo)
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    await controller.websocket_endpoint(websocket, user.user_id)
