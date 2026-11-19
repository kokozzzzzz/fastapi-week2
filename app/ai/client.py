from openai import AsyncOpenAI

from functools import lru_cache

from app.core.config import setting


@lru_cache(maxsize=1)
def get_llm_client() -> AsyncOpenAI:
    '''
    获取可复用的大模型客户端。
    '''

    api_key = setting.deepseek_api_key.strip()

    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY尚未配置，请检查.env文件。"
        )

    return AsyncOpenAI(
        api_key=api_key,
        base_url=setting.llm_base_url.rstrip("/"),
        timeout=setting.llm_timeout,
        max_retries=2,
    )

async def generate_answer(
    messages: list[dict[str,str]]
) -> str:
    """
    根据消息列表调用大模型，返回回答文本。
    """

    client = get_llm_client()

    response = await client.chat.completions.create(
        model=setting.llm_model,
        messages=messages,
    )

    if not response.choices:
        raise RuntimeError("模型没有返回有效回答，请重试")

    content = response.choices[0].message.content

    if content is None or not content.strip():
        raise RuntimeError("模型返回的回答为空。")

    return content.strip()



