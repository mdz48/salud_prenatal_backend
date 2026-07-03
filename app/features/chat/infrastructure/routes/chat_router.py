from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, WebSocket, Depends
from app.features.chat.infrastructure.controllers.chat_controller import ChatController
from app.features.chat.infrastructure.schemas.chat_schema import MessageResponse
from app.features.chat.domain.inbox_item_response import InboxItemResponse
from typing import List

router= APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/inbox", response_model=List[InboxItemResponse])
@inject
def get_inbox(
    current_user_id: int, 
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    return controller.get_inbox(current_user_id)

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
@inject
def get_chat_history(
    other_user_id: int, 
    current_user_id: int, 
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    return controller.get_chat_history(current_user_id, other_user_id)

@router.websocket("/ws/{user_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    await controller.websocket_endpoint(websocket, user_id)
