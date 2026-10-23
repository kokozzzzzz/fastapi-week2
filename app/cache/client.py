
import redis.asyncio as redis

from app.core.config import setting


redis_client = redis.Redis(
    host=setting.redis_host,
    port=setting.redis_port,
    db=setting.redis_db,
    decode_responses=True,
)




