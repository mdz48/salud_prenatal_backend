from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.chat.infrastructure.websocket_manager import manager
from app.features.chat.infrastructure.chat_repository import ChatRepository
from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.infrastructure.schemas.chat_schema import MessageResponse
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)




@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
@inject
def get_chat_history(
    other_user_id: int, 
    current_user_id: int, 
    usecase: GetHistoryUseCase = Depends(Provide[Container.get_history_use_case])
):
    # Note: current_user_id is passed as query param for testing (RBAC skipped for now)
    return usecase.execute(current_user_id, other_user_id)

@router.websocket("/ws/{user_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    usecase: SaveMessageUseCase = Depends(Provide[Container.save_message_use_case])
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # We expect a JSON payload from the client like {"receiver_id": 2, "content": "Hello"}
            data = await websocket.receive_json()
            receiver_id = data.get("receiver_id")
            content = data.get("content")
            
            if receiver_id and content:
                # Save to DB
                db_msg = usecase.execute(sender_id=user_id, receiver_id=receiver_id, content=content)
                
                # Format message to send back
                msg_payload = {
                    "message_id": db_msg.message_id,
                    "sender_id": db_msg.sender_id,
                    "receiver_id": db_msg.receiver_id,
                    "content": db_msg.content,
                    "created_at": db_msg.created_at.isoformat() if db_msg.created_at else None,
                    "is_read": db_msg.is_read
                }
                
                # Send to receiver if online
                await manager.send_personal_message(msg_payload, receiver_id)
                
                # Echo back to the sender
                await manager.send_personal_message(msg_payload, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
