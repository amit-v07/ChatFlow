from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import Optional


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    conversation_id: uuid.UUID
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field(default="text", pattern="^(text|image|file|system)$")


class MessageUpdate(BaseModel):
    """Schema for updating message status."""
    status: str = Field(..., pattern="^(sent|delivered|read|failed)$")


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    message_type: str
    status: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MessageEvent(BaseModel):
    """Schema for WebSocket message events."""
    type: str  # 'new_message', 'message_delivered', 'message_read', 'typing'
    message: Optional[MessageResponse] = None
    conversation_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
