
import json

from redis.asyncio import Redis


CACHE_LIMIT = 20
CACHE_TTL = 86400  # 24小时

def get_chat_cache_key(conversation_id: int) -> str:
    """
    生成规范的 Redis 键名
    """
    return f"chat:conversation:{conversation_id}"



async def get_cached_messages(
    redis: Redis,
    conversation_id: int,
) ->list[dict]:
    """
    从 Redis 取出历史聊天记录
    """

    key = get_chat_cache_key(conversation_id)

    values = await redis.lrange(key,0,-1)

    return [
        json.loads(value)
        for value in values
    ]


async def save_cached_message(
    redis: Redis,
    conversation_id: int,
    role: str,
    content: str,
) -> None:
    """
    把新消息存入Redis，并清理旧消息。
    """

    key = get_chat_cache_key(conversation_id)

    message = json.dumps(
        {
            "role": role,
            "content": content,
        },
        ensure_ascii=False,
    )

    async with redis.pipeline(transaction=True) as pipe:
        await pipe.rpush(key, message)
        await pipe.ltrim(key, -CACHE_LIMIT, -1)
        await pipe.expire(key, CACHE_TTL)
        await pipe.execute()


async def clear_chat_cache(
    redis: Redis,
    conversation_id: int,
) -> None:
    """
    彻底删除某个会话的缓存。
    """

    key = get_chat_cache_key(conversation_id)

    await redis.delete(key)


