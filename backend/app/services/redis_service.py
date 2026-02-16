import redis.asyncio as aioredis
from typing import Optional
from app.core.config import settings


class RedisService:
    """Redis service for caching and pub/sub."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
    
    async def connect(self):
        """Establish Redis connection."""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        self.pubsub = self.redis.pubsub()
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set a key-value pair in Redis."""
        if expire:
            await self.redis.setex(key, expire, value)
        else:
            await self.redis.set(key, value)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return await self.redis.get(key)
    
    async def delete(self, key: str):
        """Delete a key from Redis."""
        await self.redis.delete(key)
    
    async def publish(self, channel: str, message: str):
        """Publish a message to a channel."""
        await self.redis.publish(channel, message)
    
    async def subscribe(self, *channels: str):
        """Subscribe to channels."""
        await self.pubsub.subscribe(*channels)
    
    async def unsubscribe(self, *channels: str):
        """Unsubscribe from channels."""
        await self.pubsub.unsubscribe(*channels)


# Global Redis instance
redis_service = RedisService()
