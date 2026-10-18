import jwt
from pwdlib import PasswordHash
from app.core.config import setting

from datetime import (
    datetime,
    timedelta,
    timezone,
)

password_hash = PasswordHash.recommended()

def hash_password(password: str)->str:
    return password_hash.hash(password)

# 验证密码正确性
def verify_password(
    plain_password: str,
    hashed_password: str
)->bool :
    return password_hash.verify(
        plain_password,
        hashed_password
    )

# 创建登录token
def create_access_token(
    user_id: int
) -> str:
    expire = (
        datetime.now(timezone.utc) + timedelta(
            minutes=setting.access_token_expire_minutes
        )
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        setting.secret_key,
        algorithm=setting.algorithm,
    )

# 解码登录token
def decode_access_token(
    token: str
) -> int |None:
    try:
        # 验签并解密
        payload = jwt.decode(
            token,
            setting.secret_key,
            algorithms=[setting.algorithm],
        )
        # 取出 user_id (之前存的时候转成了字符串，现在转回 int)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.InvalidTokenError:
        # 如果 token 是伪造的，或者过期了，就会报错，返回 None
        return None




