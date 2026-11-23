from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# 会话表
class Conversation(Base):
    __tablename__ = "conversations"

    # 会话的唯一标识
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 用户id
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    # 会话标题
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="新对话",
    )

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    # 最近更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    # 对话内容
    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


# 消息表
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    # 消息的唯一标识
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 会话id
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 角色身份
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # 具体内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # 消息的发送时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    
    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )