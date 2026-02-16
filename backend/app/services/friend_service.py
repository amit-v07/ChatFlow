from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, or_, and_
from fastapi import HTTPException, status
import uuid
from app.models.user import User
from app.models.friend import FriendRequest, FriendRequestStatus
from app.models.friend_association import Friend
from app.models.conversation import Conversation, ConversationParticipant, ConversationType
from app.services.websocket_manager import manager as websocket_manager
from app.schemas.friend import FriendRequestCreate, FriendRequestUpdate

class FriendService:
    async def search_users(self, db: AsyncSession, query: str, current_user_id: uuid.UUID):
        # Simple search by email or username (if we had username, for now email)
        # Exclude current user
        stmt = select(User).where(
            and_(
                User.email.ilike(f"%{query}%"),
                User.id != current_user_id
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def send_friend_request(self, db: AsyncSession, request_data: FriendRequestCreate, sender_id: uuid.UUID):
        # Check if receiver exists
        receiver = await db.get(User, request_data.receiver_id)
        if not receiver:
            raise HTTPException(status_code=404, detail="User not found")

        if sender_id == request_data.receiver_id:
            raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")

        # Check existing request or friendship
        stmt = select(FriendRequest).where(
            or_(
                and_(FriendRequest.sender_id == sender_id, FriendRequest.receiver_id == request_data.receiver_id),
                and_(FriendRequest.sender_id == request_data.receiver_id, FriendRequest.receiver_id == sender_id)
            )
        )
        result = await db.execute(stmt)
        existing_request = result.scalar_one_or_none()

        if existing_request:
            if existing_request.status == FriendRequestStatus.PENDING:
                raise HTTPException(status_code=400, detail="Friend request already pending")
            if existing_request.status == FriendRequestStatus.ACCEPTED:
                raise HTTPException(status_code=400, detail="Users are already friends")

        # Create request
        new_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=request_data.receiver_id,
            status=FriendRequestStatus.PENDING
        )
        db.add(new_request)
        await db.commit()
        await db.refresh(new_request)

        # Real-time notification
        await websocket_manager.send_personal_message(
            {
                "type": "friend_request_received",
                "request_id": str(new_request.id),
                "sender_id": str(sender_id),
                # Should ideally send sender name/email too
            }
        )

        return new_request

    async def respond_to_friend_request(self, db: AsyncSession, request_id: uuid.UUID, status_update: FriendRequestUpdate, current_user_id: uuid.UUID):
        request = await db.get(FriendRequest, request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Friend request not found")

        if request.receiver_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to respond to this request")

        if request.status != FriendRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request already processed")

        request.status = status_update.status
        
        if status_update.status == FriendRequestStatus.ACCEPTED:
            # Create bi-directional friendship
            friend1 = Friend(user_id=request.sender_id, friend_id=request.receiver_id)
            friend2 = Friend(user_id=request.receiver_id, friend_id=request.sender_id)
            db.add(friend1)
            db.add(friend2)

            # Check if private conversation already exists
            # Optimized query to find common private conversation
            # For now, simplest way: check for conversation with these 2 participants
            # TODO: Improve this query
            
            # Create new private conversation
            conversation = Conversation(type=ConversationType.PRIVATE)
            db.add(conversation)
            await db.flush() # get ID

            part1 = ConversationParticipant(conversation_id=conversation.id, user_id=request.sender_id)
            part2 = ConversationParticipant(conversation_id=conversation.id, user_id=request.receiver_id)
            db.add(part1)
            db.add(part2)

            # Real-time notification
            await websocket_manager.send_personal_message(
                {
                    "type": "friend_request_accepted",
                    "friend_id": str(current_user_id),
                    "conversation_id": str(conversation.id)
                },
                str(request.sender_id)
            )

        await db.commit()
        await db.refresh(request)
        return request

    async def get_pending_requests(self, db: AsyncSession, current_user_id: uuid.UUID):
        stmt = select(FriendRequest).where(
            FriendRequest.receiver_id == current_user_id,
            FriendRequest.status == FriendRequestStatus.PENDING
        ).order_by(FriendRequest.created_at.desc())
        
        # Eager load sender
        from sqlalchemy.orm import selectinload
        stmt  = stmt.options(selectinload(FriendRequest.sender))
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_friends(self, db: AsyncSession, current_user_id: uuid.UUID):
        stmt = select(Friend).where(Friend.user_id == current_user_id).options(selectinload(Friend.friend))
        result = await db.execute(stmt)
        return result.scalars().all()


friend_service = FriendService()
