from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime
from typing import Optional
from app.models.friend import FriendRequestStatus
from app.schemas.user import UserResponse

class FriendRequestCreate(BaseModel):
    receiver_id: UUID4

class FriendRequestUpdate(BaseModel):
    status: FriendRequestStatus

class FriendRequestResponse(BaseModel):
    id: UUID4
    sender_id: UUID4
    receiver_id: UUID4
    status: FriendRequestStatus
    created_at: datetime
    sender: Optional[UserResponse] = None
    receiver: Optional[UserResponse] = None



class FriendResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    friend_id: UUID4
    created_at: datetime
    friend: Optional[UserResponse] = None

    class Config:
        from_attributes = True
