from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
    ChatMessage
)



def create_conversation(
    db: Session,
    user_id: int,
    title: str = "新对话",
) -> Conversation:
    """
    创建会话
    """

    conversation = Conversation(
        user_id = user_id,
        title = title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> ChatMessage:
    """
    保存会话信息
    """

    message = ChatMessage(
        conversation_id = conversation_id,
        role = role,
        content = content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 20,
) -> list[ChatMessage]:
    """
    得到限制内最近的消息
    """

    messages = (
        db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        )
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )

    return list(reversed(messages))


def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    """
    得到用户会话，以更新时间排序
    """

    return (
        db.query(Conversation)
        .filter(Conversation.user_id==user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )




