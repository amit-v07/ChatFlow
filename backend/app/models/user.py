from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.db.base import Base


class User(Base):
    """User model for authentication and profile."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    conversations = relationship("ConversationParticipant", back_populates="user")
    sent_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.sender_id", back_populates="sender")
    received_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.receiver_id", back_populates="receiver")
    friends = relationship("Friend", foreign_keys="Friend.user_id", back_populates="user")
    initiated_calls = relationship("CallLog", foreign_keys="CallLog.caller_id", back_populates="caller")
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
