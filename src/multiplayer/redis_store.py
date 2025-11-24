import json
import redis.asyncio as aioredis
from typing import Any
import logging

logger = logging.getLogger(__name__)


class RedisGameStore:
    """Redis-based persistent storage for game state."""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        """
        Initialise Redis store.
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: aioredis.Redis | None = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    async def save_game_state(self, lobby_id: str, state: dict[str, Any]):
        """
        Save game state to Redis.
        Args:
            lobby_id: Lobby ID
            state: Game state dictionary
        """
        if not self.redis:
            return
        
        try:
            key = f"game:{lobby_id}"
            await self.redis.set(key, json.dumps(state))
            await self.redis.expire(key, 3600) 
            logger.debug(f"Saved game state for {lobby_id}")
        except Exception as e:
            logger.error(f"Error saving game state: {e}")
    
    async def load_game_state(self, lobby_id: str) -> dict[str, Any] | None:
        """
        Load game state from Redis.
        Args:
            lobby_id: Lobby ID
        Returns:
            Game state dictionary or None
        """
        if not self.redis:
            return None
        
        try:
            key = f"game:{lobby_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error loading game state: {e}")
        
        return None
    
    async def delete_game_state(self, lobby_id: str):
        """Delete game state from Redis."""
        if not self.redis:
            return
        
        try:
            key = f"game:{lobby_id}"
            await self.redis.delete(key)
            logger.debug(f"Deleted game state for {lobby_id}")
        except Exception as e:
            logger.error(f"Error deleting game state: {e}")
    
    async def save_player_points(self, player_id: str, points: int):
        """Save player points persistently."""
        if not self.redis:
            return
        
        try:
            key = f"player:{player_id}:points"
            await self.redis.set(key, points)
            logger.debug(f"Saved points for player {player_id}: {points}")
        except Exception as e:
            logger.error(f"Error saving player points: {e}")
    
    async def load_player_points(self, player_id: str) -> int:
        """Load player points."""
        if not self.redis:
            return 0
        
        try:
            key = f"player:{player_id}:points"
            points = await self.redis.get(key)
            return int(points) if points else 0
        except Exception as e:
            logger.error(f"Error loading player points: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")