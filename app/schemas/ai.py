from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# chat请求模型
class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="用户提出的问题",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("问题不能为空")

        return value

# chat回应模型
class ChatResponse(BaseModel):
    answer: str
    model: str

# summary文本模型
class TextRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=8000,
        description="需要处理的文本",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("文本不能为空")

        return value


# 信息提取模型（继承TextRequest）
class ExtractRequest(TextRequest):
    use_few_shot: bool = Field(
        default=False,
        description="是否使用少样本提示",
    )


# 创建会话请求类
class ConversationCreate(BaseModel):
    title: str = Field(
        default="新对话",
        min_length=1,
        max_length=200,
    )


# 会话聊天请求类
class ConversationChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=8000,
    )


# 会话响应类
class ConversationResponse(BaseModel):
    id: int
    title: str


# 信息响应类
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
