from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db : Session = Depends(get_db),
) -> User:
    # 验证token真假
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 查找用户是否存在
    user = user_service.find_user(db,user_id)
    if user is None:
        raise HTTPException(
            status_code= 401,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


