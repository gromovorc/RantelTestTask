import redis.asyncio as redis
from app.core.config import settings

def create_redis():
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)