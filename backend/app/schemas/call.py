from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
import uuid


class CallInitiate(BaseModel):
    """Schema for initiating a call."""
    callee_id: uuid.UUID
    call_type: str = Field(..., pattern="^(audio|video)$")


class CallSignal(BaseModel):
    """Schema for WebRTC signaling messages."""
    type: str  # 'offer', 'answer', 'ice-candidate'
    call_id: uuid.UUID
    signal_data: Any  # SDP or ICE candidate data


class CallAction(BaseModel):
    """Schema for call actions (accept, reject, end)."""
    call_id: uuid.UUID
    action: str = Field(..., pattern="^(accept|reject|end)$")


class CallLogResponse(BaseModel):
    """Schema for call log response."""
    id: uuid.UUID
    caller_id: uuid.UUID
    callee_id: uuid.UUID
    call_type: str
    status: str
    duration_seconds: Optional[int]
    initiated_at: datetime
    accepted_at: Optional[datetime]
    ended_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CallEvent(BaseModel):
    """Schema for WebSocket call events."""
    type: str  # 'call_initiated', 'call_ringing', 'call_accepted', etc.
    call_id: Optional[uuid.UUID] = None
    caller_id: Optional[uuid.UUID] = None
    callee_id: Optional[uuid.UUID] = None
    call_type: Optional[str] = None
    signal_data: Optional[Any] = None  # For offer/answer/ICE
    timestamp: datetime = Field(default_factory=datetime.utcnow)
