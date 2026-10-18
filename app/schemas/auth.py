
from pydantic import BaseModel

# 登录请求类
class LoginRequest(BaseModel):
    username: str
    password: str

# 登录响应类
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

