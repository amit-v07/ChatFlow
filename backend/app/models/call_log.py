from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import uuid
import enum
from app.db.base import Base


class CallType(str, enum.Enum):
    """Type of call."""
    AUDIO = "audio"
    VIDEO = "video"


class CallStatus(str, enum.Enum):
    """Status of call."""
    INITIATED = "initiated"
    RINGING = "ringing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ENDED = "ended"
    MISSED = "missed"
    FAILED = "failed"


class CallLog(Base):
    """Call log model for tracking calls."""
    
    __tablename__ = "call_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    caller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    callee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    call_type: Mapped[CallType] = mapped_column(
        SQLEnum(CallType),
        nullable=False,
        default=CallType.AUDIO
    )
    status: Mapped[CallStatus] = mapped_column(
        SQLEnum(CallStatus),
        nullable=False,
        default=CallStatus.INITIATED
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    initiated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    caller: Mapped["User"] = relationship("User", foreign_keys=[caller_id])
    callee: Mapped["User"] = relationship("User", foreign_keys=[callee_id])
    
    def __repr__(self) -> str:
        return f"<CallLog {self.id} {self.caller_id} -> {self.callee_id} ({self.status})>"
