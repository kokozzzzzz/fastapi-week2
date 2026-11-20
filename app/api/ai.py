from fastapi import APIRouter,HTTPException

from openai import(
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import setting
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    TextRequest,
    ExtractRequest
)
from app.services.ai_service import (
    chat_with_ai,
    summarize_text,
    extract_key_info,
)

from collections.abc import Awaitable


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

async def _run_ai_task(task: Awaitable[str]) -> str:
    try:
        return await task
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
    except AuthenticationError as e:
        raise HTTPException(
            status_code=502,
            detail="大模型服务认证失败，请检查API Key。"
        )from e
    except RateLimitError as e:
        raise HTTPException(
            status_code=503,
            detail="模型请求受限或账户额度不足。",
        ) from e
    except APITimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail="大模型请求超时，请稍后重试"
        )from e
    except APIConnectionError as e:
        raise HTTPException(
            status_code=502,
            detail="无法连接大模型服务，请检查网络。",
        ) from e
    except APIStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"大模型服务返回错误，状态码：{e.status_code}",
        ) from e


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(data: ChatRequest):
    answer = await _run_ai_task(chat_with_ai(data.message))

    return ChatResponse(
        answer=answer,
        model=setting.llm_model,
    )

@router.post(
    "/summarize",
    response_model=ChatResponse
)
async def summarize(data: TextRequest):
    answer = await _run_ai_task(summarize_text(data.text))

    return ChatResponse(
        answer=answer,
        model=setting.llm_model,
    )

@router.post(
    "/extract",
    response_model=ChatResponse,
)
async def extract(data: ExtractRequest):

    answer = await _run_ai_task(
        extract_key_info(
            data.text,
            use_few_shot=data.use_few_shot,
        )
    )

    return ChatResponse(
        answer=answer,
        model=setting.llm_model,
    )

