from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.websocket_manager import manager
from app.services.call_service import call_service
from app.schemas.call import CallInitiate
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/call")
async def call_websocket(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for WebRTC call signaling.
    
    Connection URL: ws://localhost:8000/ws/call?token=YOUR_ACCESS_TOKEN
    
    This endpoint handles WebRTC signaling (offer/answer/ICE) but does NOT
    relay media. Media flows peer-to-peer between clients.
    
    Message types:
    - initiate_call: Start a new call
    - accept_call: Accept incoming call
    - reject_call: Reject incoming call
    - end_call: End active call
    - offer: Send WebRTC offer
    - answer: Send WebRTC answer
    - ice_candidate: Send ICE candidate
    
    Example - Initiate call:
    {
        "type": "initiate_call",
        "callee_id": "uuid",
        "call_type": "video"
    }
    
    Example - WebRTC offer:
    {
        "type": "offer",
        "call_id": "uuid",
        "signal_data": {
            "sdp": "...",
            "type": "offer"
        }
    }
    """
    user_id = None
    connection_id = None
    
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
            "message": "Connected to call signaling"
        })
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "initiate_call":
                # Initiate a new call
                callee_id = data.get("callee_id")
                call_type = data.get("call_type", "audio")
                
                # Create call log
                call_log = await call_service.initiate_call(
                    db, user_id, callee_id, call_type
                )
                
                if call_log:
                    # Notify caller
                    await websocket.send_json({
                        "type": "call_initiated",
                        "call_id": str(call_log.id),
                        "callee_id": callee_id,
                        "call_type": call_type
                    })
                    
                    # Notify callee (incoming call)
                    if manager.is_user_online(callee_id):
                        await manager.send_personal_message(
                            {
                                "type": "incoming_call",
                                "call_id": str(call_log.id),
                                "caller_id": user_id,
                                "call_type": call_type
                            },
                            callee_id
                        )
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Callee is not online"
                        })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to initiate call"
                    })
            
            elif message_type == "accept_call":
                # Accept incoming call
                call_id = data.get("call_id")
                
                success = await call_service.accept_call(db, call_id, user_id)
                
                if success:
                    call_info = call_service.get_call_info(call_id)
                    
                    # Notify caller that call was accepted
                    if call_info:
                        caller_id = call_info["caller_id"]
                        await manager.send_personal_message(
                            {
                                "type": "call_accepted",
                                "call_id": call_id
                            },
                            caller_id
                        )
                    
                    # Confirm to callee
                    await websocket.send_json({
                        "type": "call_accepted",
                        "call_id": call_id
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to accept call"
                    })
            
            elif message_type == "reject_call":
                # Reject incoming call
                call_id = data.get("call_id")
                call_info = call_service.get_call_info(call_id)
                
                success = await call_service.reject_call(db, call_id, user_id)
                
                if success and call_info:
                    # Notify caller that call was rejected
                    caller_id = call_info["caller_id"]
                    await manager.send_personal_message(
                        {
                            "type": "call_rejected",
                            "call_id": call_id
                        },
                        caller_id
                    )
                    
                    await websocket.send_json({
                        "type": "call_rejected",
                        "call_id": call_id
                    })
            
            elif message_type == "end_call":
                # End active call
                call_id = data.get("call_id")
                call_info = call_service.get_call_info(call_id)
                
                success = await call_service.end_call(db, call_id, user_id)
                
                if success and call_info:
                    # Notify the other peer
                    other_user_id = (
                        call_info["callee_id"] 
                        if user_id == call_info["caller_id"] 
                        else call_info["caller_id"]
                    )
                    
                    await manager.send_personal_message(
                        {
                            "type": "call_ended",
                            "call_id": call_id
                        },
                        other_user_id
                    )
                    
                    await websocket.send_json({
                        "type": "call_ended",
                        "call_id": call_id
                    })
            
            elif message_type == "offer":
                # WebRTC offer - relay to callee
                call_id = data.get("call_id")
                signal_data = data.get("signal_data")
                
                await call_service.relay_signal(
                    call_id, user_id, "offer", signal_data
                )
            
            elif message_type == "answer":
                # WebRTC answer - relay to caller
                call_id = data.get("call_id")
                signal_data = data.get("signal_data")
                
                await call_service.relay_signal(
                    call_id, user_id, "answer", signal_data
                )
            
            elif message_type == "ice_candidate":
                # ICE candidate - relay to other peer
                call_id = data.get("call_id")
                candidate = data.get("candidate")
                
                await call_service.relay_signal(
                    call_id, user_id, "ice_candidate", candidate
                )
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"Call WebSocket disconnected: user_id={user_id}")
    
    except Exception as e:
        logger.error(f"Call WebSocket error: {e}")
    
    finally:
        # Cleanup
        if user_id and connection_id:
            await manager.disconnect(connection_id, user_id)
