from app.db.base import Base
from app.models.user import User
from app.models.conversation import Conversation, ConversationParticipant
from app.models.message import Message
from app.models.call_log import CallLog
from app.models.friend import FriendRequest
from app.models.friend_association import Friend

# Import all models here for Alembic autogenerate
__all__ = ["Base", "User", "Conversation", "ConversationParticipant", "Message", "CallLog", "FriendRequest", "Friend"]
