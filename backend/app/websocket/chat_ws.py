from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.websocket_manager import manager
from app.services.chat_service import chat_service
from app.services.redis_service import redis_service
from app.schemas.message import MessageCreate, MessageResponse
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.
    
    Connection URL: ws://localhost:8000/ws/chat?token=YOUR_ACCESS_TOKEN
    
    Message types:
    - send_message: Send a new message
    - message_delivered: Mark message as delivered
    - message_read: Mark message as read
    - typing: Send typing indicator
    - join_conversation: Subscribe to conversation messages
    
    Example message:
    {
        "type": "send_message",
        "conversation_id": "uuid",
        "content": "Hello!",
        "message_type": "text"
    }
    """
    user_id = None
    connection_id = None
    subscribed_conversations = set()
    
    try:
        # Authenticate and connect
        user_id = await manager.connect(websocket, token)
        
        if not user_id:
            return
        
        from datetime import datetime
        connection_id = f"{user_id}_{datetime.utcnow().timestamp()}"
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "Connected to chat"
        })
        
        # Start Redis listener in background
        import asyncio
        
        async def redis_listener():
            """Listen for Redis pub/sub messages."""
            try:
                if not redis_service.pubsub:
                    return
                
                async for message in redis_service.pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        
                        # Forward to WebSocket
                        if manager.is_user_online(user_id):
                            await manager.send_personal_message(data, user_id)
            
            except Exception as e:
                logger.error(f"Redis listener error: {e}")
        
        # Start listener task
        listener_task = asyncio.create_task(redis_listener())
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            print(f"DEBUG: Received WS message: {data}", flush=True)  # DEBUG PRINT
            logger.info(f"Received WS message: {data}")
            message_type = data.get("type")
            
            if message_type == "send_message":
                print(f"DEBUG: Processing send_message: {data}", flush=True) # DEBUG PRINT
                logger.info(f"Processing send_message: {data}")
                # Send a new message
                message_data = MessageCreate(
                    conversation_id=data.get("conversation_id"),
                    content=data.get("content"),
                    message_type=data.get("message_type", "text")
                )
                
                message = await chat_service.send_message(db, message_data, user_id)
                print(f"DEBUG: Message saved: {message.id}", flush=True) # DEBUG PRINT
                logger.info(f"Message saved: {message.id}")
                
                if message:
                    # Convert to Pydantic model
                    message_response = MessageResponse.model_validate(message)
                    
                    # Emit to conversation participants
                    # We need to pass the Pydantic model or dict, but explicit conversion here helps
                    # Actually chat_service.emit... expects the object to have attributes like .id
                    # Let's check emit_to_conversation_participants implementation again.
                    # It uses message.id, message.content etc. So SQLAlchemy object is fine there.
                    # BUT we might want to log or use the dict there too.
                    
                    await chat_service.emit_to_conversation_participants(
                        db, str(message.conversation_id), message, exclude_sender=True
                    )
                    
                    # Send confirmation to sender
                    await websocket.send_json({
                        "type": "message_sent",
                        "message": message_response.model_dump(mode='json')
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to send message"
                    })
            
            elif message_type == "message_delivered":
                # Mark message as delivered
                message_id = data.get("message_id")
                success = await chat_service.update_message_status(
                    db, message_id, "delivered", user_id
                )
                
                if success:
                    await websocket.send_json({
                        "type": "status_updated",
                        "message_id": message_id,
                        "status": "delivered"
                    })
            
            elif message_type == "message_read":
                # Mark message as read
                message_id = data.get("message_id")
                success = await chat_service.update_message_status(
                    db, message_id, "read", user_id
                )
                
                if success:
                    await websocket.send_json({
                        "type": "status_updated",
                        "message_id": message_id,
                        "status": "read"
                    })
            
            elif message_type == "join_conversation":
                # Subscribe to conversation
                conversation_id = data.get("conversation_id")
                
                await chat_service.subscribe_to_conversation(
                    conversation_id, user_id
                )
                subscribed_conversations.add(conversation_id)
                logger.info(f"User {user_id} subscribed to conversation {conversation_id}")
                
                # Get recent messages
                messages = await chat_service.get_conversation_messages(
                    db, conversation_id, user_id, limit=50
                )
                
                # Convert to Pydantic models
                message_list = [MessageResponse.model_validate(msg).model_dump(mode='json') for msg in messages]
                
                await websocket.send_json({
                    "type": "conversation_history",
                    "conversation_id": conversation_id,
                    "messages": message_list
                })
            
            elif message_type == "typing":
                # Broadcast typing indicator
                conversation_id = data.get("conversation_id")
                
                await manager.broadcast({
                    "type": "typing",
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "is_typing": data.get("is_typing", True)
                }, exclude_user=user_id)
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected: user_id={user_id}")
    
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")
    
    finally:
        # Cleanup
        if user_id and connection_id:
            await manager.disconnect(connection_id, user_id)
        
        # Unsubscribe from conversations
        for conv_id in subscribed_conversations:
            try:
                await redis_service.unsubscribe(f"chat:conversation:{conv_id}")
            except:
                pass
