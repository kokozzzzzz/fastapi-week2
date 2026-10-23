from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as users_router
from app.core.config import setting
from app.core.middleware import add_process_time, log_request_time

from app.api.health import (
    router as health_router
)
from app.db.base import Base
from app.db.session import engine
from app.models import user  # noqa

from app.api.auth import router as auth_router

from app.api.external import router as external_router

from app.api.files import router as files_router

from app.api.cache import router as cache_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=setting.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(log_request_time)

#app.middleware("http")(add_process_time)

# 用户router
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "FastAPI is running"
    }


app.include_router(health_router)

# 登录注册router
app.include_router(auth_router)

# 外部请求router
app.include_router(external_router)

# 文件router
app.include_router(files_router)

# 缓存router
app.include_router(cache_router)