from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
):
    """
    WebSocket endpoint for real-time communication.
    
    Client should connect with JWT access token as query parameter:
    ws://localhost:8000/ws?token=YOUR_ACCESS_TOKEN
    
    Connection flow:
    1. Client connects with valid JWT token
    2. Server validates token and accepts connection
    3. User marked as online in Redis
    4. Presence update broadcast to other users
    5. On disconnect, user marked offline
    """
    user_id = None
    connection_id = None
    
    try:
        # Authenticate and connect
        user_id = await manager.connect(websocket, token)
        
        if not user_id:
            # Authentication failed, connection already closed
            return
        
        # Generate connection ID
        from datetime import datetime
        connection_id = f"{user_id}_{datetime.utcnow().timestamp()}"
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "message": "Connected successfully",
            "online_users": await manager.get_online_users()
        })
        
        # Listen for messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "get_online_users":
                # Send list of online users
                online_users = await manager.get_online_users()
                await websocket.send_json({
                    "type": "online_users",
                    "users": online_users
                })
            
            else:
                # Echo back for now (chat logic will be implemented later)
                logger.info(f"Received message from {user_id}: {data}")
                await websocket.send_json({
                    "type": "echo",
                    "data": data
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        # Clean up connection
        if user_id and connection_id:
            await manager.disconnect(connection_id, user_id)
