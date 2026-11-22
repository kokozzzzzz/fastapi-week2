from app.ai.client import generate_answer,stream_answer
from app.ai.prompts import (
    build_chat_messages,
    build_extract_messages,
    build_summary_messages,
)


async def chat_with_ai(message: str) -> str:
    """
    AI聊天业务逻辑。
    """

    messages = build_chat_messages(message)

    answer = await generate_answer(messages)
    return answer


async def stream_chat_with_ai(message: str):
    """
    流式AI聊天业务逻辑
    """

    messages = build_chat_messages(message)

    async for chunk in stream_answer(messages):
        yield chunk




async def summarize_text(text: str) -> str:
    """
    AI文本总结
    """
    messages =build_summary_messages(text)

    answer = await generate_answer(messages,temperature=0.2)
    return answer

async def extract_key_info(
    text: str,
    use_few_shot: bool = False,
) -> str:
    '''
    AI信息提取
    '''

    messages = build_extract_messages(
        text,
        use_few_shot=use_few_shot
    )

    answer = await generate_answer(messages,temperature=0.2)
    return answer



