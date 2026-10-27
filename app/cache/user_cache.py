
import json

from app.cache.client import redis_client
from app.core.config import setting

def user_cache_key(user_id: int)->str:
    return f"user:{user_id}"

# 添加用户缓存
async def set_user_cache(
    user_id: int,
    data: dict,
)-> None:

    key = user_cache_key(user_id)

    await redis_client.set(
        key,
        json.dumps(data),
        ex=setting.user_cache_ttl,
    )

# 得到用户缓存信息
async def get_user_cache(
    user_id: int
) -> dict | None:

    key = user_cache_key(user_id)

    cached = await redis_client.get(key)

    if cached is None:
        return None

    return json.loads(cached)

# 删除用户缓存
async def delete_user_cache(
    user_id: int
)-> None:
    key = user_cache_key(user_id)

    await redis_client.delete(key)








