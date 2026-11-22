from openai import AsyncOpenAI

from functools import lru_cache

from app.core.config import setting

from collections.abc import AsyncIterator


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
    messages: list[dict[str,str]],
    temperature: float | None = None,
) -> str:
    """
    根据消息列表调用大模型，返回回答文本。
    """

    client = get_llm_client()

    if temperature is None:
        response = await client.chat.completions.create(
            model=setting.llm_model,
            messages=messages,
        )
    else:
        if not 0 <= temperature <=2:
            raise ValueError("temperature必须再0-2之间")

        response = await client.chat.completions.create(
            model=setting.llm_model,
            messages=messages,
            temperature=temperature,
            extra_body={
                "thinking":{
                    "type": "disabled"
                }
            }
        )
    
    

    if not response.choices:
        raise RuntimeError("模型没有返回有效回答，请重试")

    content = response.choices[0].message.content

    if content is None or not content.strip():
        raise RuntimeError("模型返回的回答为空。")

    return content.strip()


async def stream_answer(
    messages: list[dict[str,str]]
) -> AsyncIterator[str]:
    '''
    流式调用大模型，逐段返回回答文本。
    '''

    client = get_llm_client()

    stream = await client.chat.completions.create(
        model=setting.llm_model,
        messages=messages,
        stream=True,
        extra_body={
            "thinking": {
                "type": "disabled"
            }
        }
    )

    try:
        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

    finally:
        await stream.close()

