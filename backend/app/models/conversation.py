from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
import uuid
import enum
from app.db.base import Base


class ConversationType(str, enum.Enum):
    """Type of conversation."""
    PRIVATE = "private"
    GROUP = "group"


class Conversation(Base):
    """Conversation model for chat."""
    
    __tablename__ = "conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[ConversationType] = mapped_column(
        SQLEnum(ConversationType),
        nullable=False,
        default=ConversationType.PRIVATE
    )
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    participants: Mapped[List["ConversationParticipant"]] = relationship(
        "ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Conversation {self.id} ({self.type})>"


class ConversationParticipant(Base):
    """Participants in a conversation."""
    
    __tablename__ = "conversation_participants"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="participants")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<ConversationParticipant conversation={self.conversation_id} user={self.user_id}>"
