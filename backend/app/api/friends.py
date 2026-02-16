from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.friend import FriendRequestCreate, FriendRequestUpdate, FriendRequestResponse, FriendResponse
from app.core.dependencies import get_current_active_user
from app.services.friend_service import friend_service

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/request", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    request: FriendRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a friend request to another user."""
    return await friend_service.send_friend_request(db, request, current_user.id)

@router.put("/request/{request_id}", response_model=FriendRequestResponse)
async def respond_to_friend_request(
    request_id: uuid.UUID,
    update: FriendRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept or reject a friend request."""
    return await friend_service.respond_to_friend_request(db, request_id, update, current_user.id)

@router.get("/requests", response_model=List[FriendRequestResponse])
async def get_pending_requests(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List pending friend requests received by the current user."""
    return await friend_service.get_pending_requests(db, current_user.id)

@router.get("/", response_model=List[FriendResponse])
async def get_friends(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all friends."""
    return await friend_service.get_friends(db, current_user.id)

# User search endpoint (could be in users router, but part of friend flow)
@router.get("/search", response_model=List[UserResponse])
async def search_users(
    query: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search users by email (or username)."""
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Search query too short")
    return await friend_service.search_users(db, query, current_user.id)
