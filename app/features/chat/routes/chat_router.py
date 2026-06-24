from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.chat.services.chat_service import chat_service, manager
from app.features.chat.schemas.chat_schema import MessageResponse
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
def get_chat_history(other_user_id: int, current_user_id: int, db: Session = Depends(get_db)):
    # Note: current_user_id is passed as query param for testing (RBAC skipped for now)
    return chat_service.get_conversation(db, current_user_id, other_user_id)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # We expect a JSON payload from the client like {"receiver_id": 2, "content": "Hello"}
            data = await websocket.receive_json()
            receiver_id = data.get("receiver_id")
            content = data.get("content")
            
            if receiver_id and content:
                # Save to DB
                db_msg = chat_service.save_message(db, sender_id=user_id, receiver_id=receiver_id, content=content)
                
                # Format message to send back
                msg_payload = {
                    "message_id": db_msg.message_id,
                    "sender_id": db_msg.sender_id,
                    "receiver_id": db_msg.receiver_id,
                    "content": db_msg.content,
                    "created_at": db_msg.created_at.isoformat(),
                    "is_read": db_msg.is_read
                }
                
                # Send to receiver if online
                await manager.send_personal_message(msg_payload, receiver_id)
                
                # Echo back to the sender
                await manager.send_personal_message(msg_payload, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
