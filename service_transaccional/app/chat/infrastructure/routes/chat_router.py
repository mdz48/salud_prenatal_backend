from dependency_injector.wiring import inject, Provide
from container import Container
from salud_prenatal_shared_core.auth_dependencies import get_current_user, HEADER_USER_ID
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity
from fastapi import APIRouter, WebSocket, WebSocketException, Depends, status
from app.chat.infrastructure.controllers.chat_controller import ChatController
from app.chat.infrastructure.schemas.chat_schema import MessageResponse
from app.chat.domain.inbox_item_response import InboxItemResponse
from app.chat.domain.dtos import ChatUser
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
    controller: ChatController = Depends(Provide[Container.chat_controller]),
):
    # Identidad inyectada por el edge: el ForwardAuth ya validó el `?token=` del
    # upgrade (lo lee de X-Forwarded-Uri) antes de que Traefik enrutara aquí. El
    # cliente sigue mandando ?token= en la URL; este servicio ya no lo mira.
    user_id_raw = websocket.headers.get(HEADER_USER_ID, "").strip()
    if not user_id_raw:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        user_id = int(user_id_raw)
    except ValueError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    await controller.websocket_endpoint(websocket, user_id)
