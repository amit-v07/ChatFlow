from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from app.models.conversation import ConversationType
from app.schemas.user import UserResponse

class MessageSchema(BaseModel):
    id: UUID4
    conversation_id: UUID4
    sender_id: UUID4
    content: str
    message_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationParticipantSchema(BaseModel):
    user_id: UUID4
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: UUID4
    type: ConversationType
    name: Optional[str] = None
    created_at: datetime
    participants: List[ConversationParticipantSchema] = []
    messages: List[MessageSchema] = [] # Optional, maybe just last message

    class Config:
        from_attributes = True
