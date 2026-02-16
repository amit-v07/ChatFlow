from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ConversationResponse
from app.core.dependencies import get_current_active_user
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for the current user."""
    return await chat_service.get_user_conversations(db, current_user.id)

    return await chat_service.get_user_conversations(db, current_user.id)

import pydantic

class CreatePrivateChatRequest(pydantic.BaseModel):
    friend_id: uuid.UUID

@router.post("/private", response_model=ConversationResponse)
async def create_private_chat(
    request: CreatePrivateChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get or create a private conversation with a friend."""
    return await chat_service.get_or_create_private_conversation(db, current_user.id, request.friend_id)
