

from fastapi import APIRouter, Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# 注册API
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    user = auth_service.register_user(db,data)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="用户已经存在"
        )

    return user


# 登录API
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    #data: LoginRequest,
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session=Depends(get_db), 
):
    user = auth_service.authenticate_user(db,data.username,data.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="账号或密码不正确"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# 获取当前用户信息
@router.get(
    "/me",
    response_model=UserResponse
)
def read_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


