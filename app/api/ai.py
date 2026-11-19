from fastapi import APIRouter,HTTPException

from openai import(
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import setting
from app.schemas.ai import ChatRequest,ChatResponse
from app.services.ai_service import chat_with_ai


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

@router.post("/chat",response_model=ChatResponse)
async def chat(data: ChatRequest):
    try:
        answer = await chat_with_ai(data.message)

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

    return ChatResponse(
        answer=answer,
        model=setting.llm_model,
    )



