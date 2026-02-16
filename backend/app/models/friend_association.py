from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class Friend(Base):
    """
    Represents an accepted friendship between two users.
    Since friendship is bidirectional, we might need two rows or one row with bidirectional query.
    For simplicity, we can store two rows for each friendship (A->B and B->A) to simplify querying "my friends".
    Or store one row (A, B) where A < B to avoid duplicates.
    
    Given the user request 'user_id' and 'friend_id', it implies a directional or explicit link.
    Storing two rows allows easy 'SELECT * FROM friends WHERE user_id = :me' to get all friends.
    """
    __tablename__ = "friends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="friends")
    friend = relationship("User", foreign_keys=[friend_id])
