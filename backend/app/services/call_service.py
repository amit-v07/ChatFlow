from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict
import logging
from datetime import datetime
from app.models.call_log import CallLog, CallStatus, CallType
from app.models.user import User
from app.schemas.call import CallLogResponse
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)


class CallService:
    """Service for handling call signaling and logging."""
    
    def __init__(self):
        # Track active calls: call_id -> {caller_id, callee_id, call_type}
        self.active_calls: Dict[str, dict] = {}
    
    async def initiate_call(
        self,
        db: AsyncSession,
        caller_id: str,
        callee_id: str,
        call_type: str
    ) -> Optional[CallLogResponse]:
        """
        Initiate a new call.
        
        Args:
            db: Database session
            caller_id: Caller user ID
            callee_id: Callee user ID
            call_type: 'audio' or 'video'
            
        Returns:
            Created call log or None if failed
        """
        try:
            # Verify both users exist
            caller = await db.execute(select(User).where(User.id == caller_id))
            callee = await db.execute(select(User).where(User.id == callee_id))
            
            if not caller.scalar_one_or_none() or not callee.scalar_one_or_none():
                logger.warning(f"Invalid caller or callee")
                return None
            
            # Create call log
            call_log = CallLog(
                caller_id=caller_id,
                callee_id=callee_id,
                call_type=CallType(call_type),
                status=CallStatus.INITIATED
            )
            
            db.add(call_log)
            await db.commit()
            await db.refresh(call_log)
            
            # Track active call
            self.active_calls[str(call_log.id)] = {
                "caller_id": caller_id,
                "callee_id": callee_id,
                "call_type": call_type
            }
            
            logger.info(f"Call initiated: {call_log.id} from {caller_id} to {callee_id}")
            return CallLogResponse.model_validate(call_log)
            
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            await db.rollback()
            return None
    
    async def accept_call(
        self,
        db: AsyncSession,
        call_id: str,
        user_id: str
    ) -> bool:
        """
        Accept a call.
        
        Args:
            db: Database session
            call_id: Call ID
            user_id: User accepting the call
            
        Returns:
            True if accepted successfully
        """
        try:
            # Get call log
            result = await db.execute(select(CallLog).where(CallLog.id == call_id))
            call_log = result.scalar_one_or_none()
            
            if not call_log:
                return False
            
            # Verify user is the callee
            if str(call_log.callee_id) != user_id:
                logger.warning(f"User {user_id} not authorized to accept call {call_id}")
                return False
            
            # Update status
            call_log.status = CallStatus.ACCEPTED
            call_log.accepted_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Call {call_id} accepted by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting call: {e}")
            await db.rollback()
            return False
    
    async def reject_call(
        self,
        db: AsyncSession,
        call_id: str,
        user_id: str
    ) -> bool:
        """
        Reject a call.
        
        Args:
            db: Database session
            call_id: Call ID
            user_id: User rejecting the call
            
        Returns:
            True if rejected successfully
        """
        try:
            result = await db.execute(select(CallLog).where(CallLog.id == call_id))
            call_log = result.scalar_one_or_none()
            
            if not call_log:
                return False
            
            # Verify user is the callee
            if str(call_log.callee_id) != user_id:
                return False
            
            # Update status
            call_log.status = CallStatus.REJECTED
            call_log.ended_at = datetime.utcnow()
            
            await db.commit()
            
            # Remove from active calls
            self.active_calls.pop(call_id, None)
            
            logger.info(f"Call {call_id} rejected by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting call: {e}")
            await db.rollback()
            return False
    
    async def end_call(
        self,
        db: AsyncSession,
        call_id: str,
        user_id: str
    ) -> bool:
        """
        End an active call.
        
        Args:
            db: Database session
            call_id: Call ID
            user_id: User ending the call
            
        Returns:
            True if ended successfully
        """
        try:
            result = await db.execute(select(CallLog).where(CallLog.id == call_id))
            call_log = result.scalar_one_or_none()
            
            if not call_log:
                return False
            
            # Verify user is participant
            if str(call_log.caller_id) != user_id and str(call_log.callee_id) != user_id:
                return False
            
            # Calculate duration if call was accepted
            if call_log.accepted_at:
                duration = (datetime.utcnow() - call_log.accepted_at).total_seconds()
                call_log.duration_seconds = int(duration)
            
            # Update status
            call_log.status = CallStatus.ENDED
            call_log.ended_at = datetime.utcnow()
            
            await db.commit()
            
            # Remove from active calls
            self.active_calls.pop(call_id, None)
            
            logger.info(f"Call {call_id} ended by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            await db.rollback()
            return False
    
    async def relay_signal(
        self,
        call_id: str,
        from_user_id: str,
        signal_type: str,
        signal_data: any
    ):
        """
        Relay WebRTC signaling data between peers.
        
        Args:
            call_id: Call ID
            from_user_id: User sending the signal
            signal_type: Type of signal ('offer', 'answer', 'ice-candidate')
            signal_data: Signal data (SDP or ICE candidate)
        """
        try:
            # Get call info
            call_info = self.active_calls.get(call_id)
            
            if not call_info:
                logger.warning(f"Call {call_id} not found in active calls")
                return
            
            # Determine recipient (the other peer)
            if from_user_id == call_info["caller_id"]:
                to_user_id = call_info["callee_id"]
            elif from_user_id == call_info["callee_id"]:
                to_user_id = call_info["caller_id"]
            else:
                logger.warning(f"User {from_user_id} not in call {call_id}")
                return
            
            # Send signal to recipient
            if manager.is_user_online(to_user_id):
                await manager.send_personal_message(
                    {
                        "type": f"call_{signal_type}",
                        "call_id": call_id,
                        "signal_data": signal_data
                    },
                    to_user_id
                )
                logger.debug(f"Relayed {signal_type} from {from_user_id} to {to_user_id}")
            else:
                logger.warning(f"Recipient {to_user_id} not online")
        
        except Exception as e:
            logger.error(f"Error relaying signal: {e}")
    
    def is_call_active(self, call_id: str) -> bool:
        """Check if a call is active."""
        return call_id in self.active_calls
    
    def get_call_info(self, call_id: str) -> Optional[dict]:
        """Get active call information."""
        return self.active_calls.get(call_id)


# Global call service instance
call_service = CallService()
