from app.ai.client import generate_answer


SYSTEM_PROMPT = """
你是一个严谨、准确、清晰的中文AI助手。

回答要求：
1. 优先使用中文回答。
2. 尽量保证信息准确。
3. 对复杂问题分点解释。
4. 如果不确定，不要编造信息。
"""


async def chat_with_ai(message: str) -> str:
    """
    AI聊天业务逻辑。
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    answer = await generate_answer(messages)

    return answer