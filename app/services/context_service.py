
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.services.conversation_service import get_recent_messages
from app.cache.chat_cache import get_cached_messages
from app.ai.prompts import CHAT_SYSTEM_PROMPT

from app.cache.chat_cache import CACHE_TTL



async def build_conversation_messages(
    db: Session,
    redis: Redis,
    conversation_id: int,
    user_message: str,
) -> list[dict[str, str]]:
    """
    补全上下文+当前问题
    形成完整提示词
    """

    # 1. 优先读取Redis缓存
    history = await get_cached_messages(
        redis,
        conversation_id,
    )

    # 2. 缓存不存在时，从MySQL读取
    if not history:

        db_messages = get_recent_messages(
            db,
            conversation_id,
            limit=20,
        )

        history = [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in db_messages
        ]

        # 将数据库历史重新写入Redis
        if history:
            from app.cache.chat_cache import (
                get_chat_cache_key,
            )

            key = get_chat_cache_key(conversation_id)

            async with redis.pipeline(transaction=True) as pipe:
                for item in history:
                    import json

                    pipe.rpush(
                        key,
                        json.dumps(
                            item,
                            ensure_ascii=False,
                        ),
                    )

                pipe.expire(key, CACHE_TTL)
                await pipe.execute()

    # 3. 构造Messages
    messages = [
        {
            "role": "system",
            "content": CHAT_SYSTEM_PROMPT,
        }
    ]

    history = trim_history_by_chars(history)
    
    messages.extend(history)

    # 4. 添加当前用户问题
    messages.append({
        "role": "user",
        "content": user_message,
    })

    return messages



# Token预算策略初引入
MAX_HISTORY_CHARS = 12000


def trim_history_by_chars(
    history: list[dict[str, str]],
) -> list[dict[str, str]]:

    selected = []
    total_chars = 0

    for message in reversed(history):

        content = message["content"]
        current_length = len(content)

        if total_chars + current_length > MAX_HISTORY_CHARS:
            break

        selected.append(message)
        total_chars += current_length

    selected.reverse()

    return selected


