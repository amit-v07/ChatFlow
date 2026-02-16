from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import Optional, List


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    type: str = Field(..., pattern="^(private|group)$")
    participant_ids: List[uuid.UUID] = Field(..., min_length=1)
    name: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: uuid.UUID
    type: str
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithParticipants(BaseModel):
    """Schema for conversation with participants."""
    id: uuid.UUID
    type: str
    name: Optional[str]
    created_at: datetime
    participant_ids: List[uuid.UUID]
    
    class Config:
        from_attributes = True
