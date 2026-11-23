from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException,
    Request
)
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.db.session import get_db
from app.cache.client import get_redis
from app.api.auth import get_current_user

from app.models.user import User
from app.schemas.ai import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
    ConversationChatRequest
)

from app.models.conversation import Conversation, ChatMessage

from app.services.conversation_service import (
    create_conversation,
    get_user_conversations,
    get_recent_messages,
)

from collections.abc import AsyncGenerator

from fastapi.sse import (
    EventSourceResponse,
    ServerSentEvent,
)

from app.schemas.ai import ConversationChatRequest

from app.services.conversation_chat_service import (
    stream_chat_in_conversation,
)



router = APIRouter(
    prefix="/ai/conversations",
    tags=["AI Conversations"],
)


@router.post("", response_model=ConversationResponse)
def create_new_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新会话
    """
    
    conversation = create_conversation(
        db,
        current_user.id,
        data.title,
    )

    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户会话列表
    """
    
    return get_user_conversations(
        db,
        current_user.id,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取某个会话的历史消息
    """

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或无权访问",
        )

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.conversation_id == conversation_id
        )
        .order_by(ChatMessage.id.asc())
        .all()
    )


@router.post(
    "/{conversation_id}/chat/stream",
    response_class=EventSourceResponse,
)
async def conversation_chat_stream(
    conversation_id: int,
    data: ConversationChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user) 
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或无权访问",
        )

    try:
        async for chunk in stream_chat_in_conversation(
            db,
            redis,
            conversation_id,
            data.message,
        ):

            if await request.is_disconnected():
                break

            yield ServerSentEvent(
                event="delta",
                data={
                    "type": "delta",
                    "content": chunk,
                },
            )

        else:
            yield ServerSentEvent(
                event="done",
                data={"type": "done"},
            )

    except Exception:
        yield ServerSentEvent(
            event="error",
            data={
                "type": "error",
                "message": "本轮对话处理失败，请稍后重试。",
            },
        )





