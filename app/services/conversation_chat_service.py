
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.services.context_service import (
    build_conversation_messages,
)
from app.services.conversation_service import save_message
from app.cache.chat_cache import save_cached_message
from app.ai.client import generate_answer

from app.ai.client import stream_answer


async def chat_in_conversation(
    db: Session,
    redis: Redis,
    conversation_id: int,
    user_message: str,
) -> str:
    """
    在指定的聊天会话中，完成一轮AI对话
    """

    # 得到完整提示词
    messages = await build_conversation_messages(
        db,
        redis,
        conversation_id,
        user_message,
    )

    # 请求大模型
    answer = await generate_answer(messages)

    # 保存用户消息
    save_message(
        db,
        conversation_id,
        "user",
        user_message,
    )

    # 保存AI回答
    save_message(
        db,
        conversation_id,
        "assistant",
        answer,
    )

    # 更新Redis缓存
    await save_cached_message(
        redis,
        conversation_id,
        "user",
        user_message,
    )

    await save_cached_message(
        redis,
        conversation_id,
        "assistant",
        answer,
    )

    return answer



async def stream_chat_in_conversation(
    db: Session,
    redis: Redis,
    conversation_id: int,
    user_message: str,
):
    """
    (流式)在指定的聊天会话中，完成一轮AI对话
    """
  
    messages = await build_conversation_messages(
        db,
        redis,
        conversation_id,
        user_message,
    )

    # 先保存用户消息，保证流式中断时也保留提问
    save_message(
        db,
        conversation_id,
        "user",
        user_message,
    )

    await save_cached_message(
        redis,
        conversation_id,
        "user",
        user_message,
    )

    answer_parts = []

    async for chunk in stream_answer(messages):
        answer_parts.append(chunk)
        yield chunk

    answer = "".join(answer_parts)

    if answer:
        save_message(
            db,
            conversation_id,
            "assistant",
            answer,
        )

        await save_cached_message(
            redis,
            conversation_id,
            "assistant",
            answer,
        )



