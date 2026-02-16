from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload, aliased
from fastapi import HTTPException
import uuid
from typing import List

from app.models.conversation import Conversation, ConversationParticipant, ConversationType
from app.models.message import Message

class ChatService:
    async def create_conversation(self, db: AsyncSession, participant_ids: List[uuid.UUID], type: ConversationType = ConversationType.PRIVATE):
        conversation = Conversation(type=type)
        db.add(conversation)
        await db.flush()

        for user_id in participant_ids:
            participant = ConversationParticipant(conversation_id=conversation.id, user_id=user_id)
            db.add(participant)
        
        await db.commit()
        await db.refresh(conversation)
        
        # Re-fetch with participants to ensure they are loaded for response model
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation.id)
            .options(
                selectinload(Conversation.participants).selectinload(ConversationParticipant.user)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def get_or_create_private_conversation(self, db: AsyncSession, user_id_1: uuid.UUID, user_id_2: uuid.UUID):
        # Check if conversation exists
        stmt = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(
                Conversation.type == ConversationType.PRIVATE,
                ConversationParticipant.user_id.in_([user_id_1, user_id_2])
            )
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.user_id) == 2)
        )
        
        # This query might be imperfect if checking specifically for *only* these two.
        # Better: Find conversations where both are participants.
        
        # Proper query:
        # Find conversations ID where user 1 is participant AND user 2 is participant
        c1 = aliased(ConversationParticipant)
        c2 = aliased(ConversationParticipant)
        stmt = (
            select(Conversation)
            .join(c1, Conversation.id == c1.conversation_id)
            .join(c2, Conversation.id == c2.conversation_id)
            .where(
                Conversation.type == ConversationType.PRIVATE,
                c1.user_id == user_id_1,
                c2.user_id == user_id_2
            )
            .options(
                selectinload(Conversation.participants).selectinload(ConversationParticipant.user),
                selectinload(Conversation.messages)
            )
        )
        
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            return conversation
            
        return await self.create_conversation(db, [user_id_1, user_id_2], ConversationType.PRIVATE)

    async def get_user_conversations(self, db: AsyncSession, user_id: uuid.UUID):
        # Get all conversations for the user with participants and latest message
        stmt = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(ConversationParticipant.user_id == user_id)
            .options(
                selectinload(Conversation.participants).selectinload(ConversationParticipant.user),
                selectinload(Conversation.messages)  # This might be too heavy, improved below
            )
        )
        
        # Optimized query to fetch conversations ordered by latest message
        # For simplicity, we'll fetch conversations and sort in Python or simple query first
        # Ideally: JOIN messages and ORDER BY created_at DESC
        
        result = await db.execute(stmt)
        conversations = result.scalars().all()
        return conversations

    async def send_message(self, db: AsyncSession, message_data, sender_id: uuid.UUID):
        # Check if user is participant
        stmt = select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == message_data.conversation_id,
            ConversationParticipant.user_id == sender_id
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not a participant")

        msg = Message(
            conversation_id=message_data.conversation_id,
            sender_id=sender_id,
            content=message_data.content,
            message_type=message_data.message_type,
            status="sent"
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    async def get_conversation_messages(self, db: AsyncSession, conversation_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50, offset: int = 0):
        # Verify participation
        stmt = select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
             raise HTTPException(status_code=403, detail="Not a participant")

        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(desc(Message.created_at)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_message_status(self, db: AsyncSession, message_id: uuid.UUID, status: str, user_id: uuid.UUID):
        msg = await db.get(Message, message_id)
        if not msg:
            return False
        
        # Ensure user is recipient (not sender) - logic simplified
        if msg.sender_id == user_id:
            return False

        if status == "delivered" and msg.status == "sent":
            msg.status = "delivered"
            msg.delivered_at = func.now()
        elif status == "read":
            msg.status = "read"
            msg.read_at = func.now()
        
        await db.commit()
        return True

    # Import circular dependency locally if needed or rely on ID check
    async def emit_to_conversation_participants(self, db: AsyncSession, conversation_id: str, message: Message, exclude_sender: bool = False):
        from app.services.websocket_manager import manager
        
        # Get participants
        stmt = select(ConversationParticipant).where(ConversationParticipant.conversation_id == uuid.UUID(conversation_id))
        result = await db.execute(stmt)
        participants = result.scalars().all()
        
        message_data = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": {
                "id": str(message.id),
                "content": message.content,
                "sender_id": str(message.sender_id),
                "created_at": message.created_at.isoformat(),
                "message_type": message.message_type
            }
        }
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Emitting message {message.id} for conversation {conversation_id} to {len(participants)} participants")
        
        for p in participants:
            str_user_id = str(p.user_id)
            if exclude_sender and str_user_id == str(message.sender_id):
                logger.info(f"Skipping sender {str_user_id}")
                continue
            
            logger.info(f"Sending to participant {str_user_id}")
            await manager.send_personal_message(message_data, str_user_id)

    async def subscribe_to_conversation(self, conversation_id: str, user_id: str, websocket):
        from app.services.redis_service import redis_service
        await redis_service.subscribe(f"chat:conversation:{conversation_id}", websocket)

chat_service = ChatService()
