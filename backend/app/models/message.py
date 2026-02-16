from sqlalchemy import String, ForeignKey, DateTime, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import uuid
import enum
from app.db.base import Base


class MessageType(str, enum.Enum):
    """Type of message."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class MessageStatus(str, enum.Enum):
    """Delivery status of message."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """Message model for chat."""
    
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType),
        nullable=False,
        default=MessageType.TEXT
    )
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus),
        nullable=False,
        default=MessageStatus.SENT
    )
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    
    def __repr__(self) -> str:
        return f"<Message {self.id} from {self.sender_id}>"
