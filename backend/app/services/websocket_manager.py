from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional, Set
import json
import logging
from datetime import datetime
from app.core.security import decode_token
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with JWT authentication and Redis presence tracking.
    
    Features:
    - JWT token validation on connection
    - User -> WebSocket connection mapping
    - Redis-based presence tracking
    - Graceful disconnect handling
    - Message broadcasting
    """
    
    def __init__(self):
        # user_id -> WebSocket mapping
        self.active_connections: Dict[str, WebSocket] = {}
        
        # user_id -> set of connection IDs (for multiple devices)
        self.user_connections: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, token: str) -> Optional[str]:
        """
        Accept WebSocket connection and validate JWT token.
        
        Args:
            websocket: WebSocket connection instance
            token: JWT access token from client
            
        Returns:
            user_id if successful, None if authentication fails
        """
        # Decode and validate token
        payload = decode_token(token)
        
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            logger.warning("WebSocket connection rejected: Invalid token")
            return None
        
        # Verify token type
        if payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token type")
            logger.warning("WebSocket connection rejected: Invalid token type")
            return None
        
        # Extract user info
        user_id = payload.get("user_id")
        email = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token payload")
            logger.warning("WebSocket connection rejected: Missing user_id")
            return None
        
        # Accept connection
        await websocket.accept()
        
        # Store connection
        connection_id = f"{user_id}_{datetime.utcnow().timestamp()}"
        self.active_connections[connection_id] = websocket
        
        # Track user connections (support multiple devices)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Mark user as online in Redis
        await self._set_user_online(user_id, email)
        
        logger.info(f"WebSocket connected: user_id={user_id}, email={email}, connection_id={connection_id}")
        
        # Broadcast presence update
        await self._broadcast_presence_update(user_id, "online")
        
        return user_id
    
    async def disconnect(self, connection_id: str, user_id: str):
        """
        Handle WebSocket disconnection and cleanup.
        
        Args:
            connection_id: Unique connection identifier
            user_id: User ID associated with the connection
        """
        # Remove connection
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Update user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            
            # If no more connections for this user, mark as offline
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                await self._set_user_offline(user_id)
                await self._broadcast_presence_update(user_id, "offline")
        
        logger.info(f"WebSocket disconnected: user_id={user_id}, connection_id={connection_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send message to a specific user (all their connections).
        
        Args:
            message: Message data to send
            user_id: Target user ID
        """
        if user_id not in self.user_connections:
            print(f"DEBUG: Cannot send message: user {user_id} not connected", flush=True)
            logger.warning(f"Cannot send message: user {user_id} not connected (not in user_connections)")
            return
        
        message_json = json.dumps(message)
        connection_ids = self.user_connections[user_id]
        print(f"DEBUG: Sending to user {user_id} via {len(connection_ids)} connections: {connection_ids}", flush=True)
        logger.info(f"Sending message to user {user_id} via {len(connection_ids)} connections: {connection_ids}")
        
        # Send to all user's connections
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(message_json)
                    print(f"DEBUG: Successfully sent to connection {connection_id}", flush=True)
                    logger.info(f"Successfully sent to connection {connection_id}")
                except Exception as e:
                    print(f"DEBUG: Error sending message to {connection_id}: {e}", flush=True)
                    logger.error(f"Error sending message to {connection_id}: {e}")
            else:
                print(f"DEBUG: Connection {connection_id} inactive", flush=True)
                logger.warning(f"Connection {connection_id} in user_connections but not active_connections")
    
    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message data to broadcast
            exclude_user: Optional user_id to exclude from broadcast
        """
        message_json = json.dumps(message)
        
        for connection_id, websocket in self.active_connections.items():
            # Extract user_id from connection_id
            user_id = connection_id.split("_")[0]
            
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
    
    async def broadcast_to_users(self, message: dict, user_ids: list):
        """
        Broadcast message to specific users.
        
        Args:
            message: Message data to send
            user_ids: List of user IDs to send to
        """
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def _set_user_online(self, user_id: str, email: str):
        """
        Mark user as online in Redis.
        
        Args:
            user_id: User ID
            email: User email
        """
        try:
            # Store user presence with metadata
            presence_key = f"presence:user:{user_id}"
            presence_data = json.dumps({
                "user_id": user_id,
                "email": email,
                "status": "online",
                "last_seen": datetime.utcnow().isoformat()
            })
            
            await redis_service.set(presence_key, presence_data)
            
            # Add to online users set
            await redis_service.redis.sadd("presence:online_users", user_id)
            
            logger.debug(f"User {user_id} marked as online in Redis")
        except Exception as e:
            logger.error(f"Error setting user online in Redis: {e}")
    
    async def _set_user_offline(self, user_id: str):
        """
        Mark user as offline in Redis.
        
        Args:
            user_id: User ID
        """
        try:
            # Update presence status
            presence_key = f"presence:user:{user_id}"
            presence_data = await redis_service.get(presence_key)
            
            if presence_data:
                data = json.loads(presence_data)
                data["status"] = "offline"
                data["last_seen"] = datetime.utcnow().isoformat()
                await redis_service.set(presence_key, json.dumps(data), expire=86400)  # Keep for 24h
            
            # Remove from online users set
            await redis_service.redis.srem("presence:online_users", user_id)
            
            logger.debug(f"User {user_id} marked as offline in Redis")
        except Exception as e:
            logger.error(f"Error setting user offline in Redis: {e}")
    
    async def _broadcast_presence_update(self, user_id: str, status: str):
        """
        Broadcast presence update via Redis pub/sub.
        
        Args:
            user_id: User ID
            status: 'online' or 'offline'
        """
        try:
            presence_update = json.dumps({
                "type": "presence_update",
                "user_id": user_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await redis_service.publish("presence:updates", presence_update)
            logger.debug(f"Published presence update for user {user_id}: {status}")
        except Exception as e:
            logger.error(f"Error broadcasting presence update: {e}")
    
    async def get_online_users(self) -> list:
        """
        Get list of currently online user IDs.
        
        Returns:
            List of online user IDs
        """
        try:
            online_users = await redis_service.redis.smembers("presence:online_users")
            return list(online_users) if online_users else []
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return []
    
    async def is_user_online(self, user_id: str) -> bool:
        """
        Check if a user is currently online.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is online, False otherwise
        """
        return user_id in self.user_connections
    
    def get_connection_count(self) -> int:
        """
        Get total number of active WebSocket connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def get_user_count(self) -> int:
        """
        Get number of unique users connected.
        
        Returns:
            Number of unique connected users
        """
        return len(self.user_connections)


# Global connection manager instance
manager = ConnectionManager()
