from fastapi import FastAPI

from app.api.users import router as users_router
from app.core.config import setting
from app.core.middleware import add_process_time

from app.api.health import (
    router as health_router
)
from app.db.base import Base
from app.db.session import engine
from app.models import user  # noqa

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=setting.app_name,
    version="0.1.0",
)

app.middleware("http")(add_process_time)

app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "FastAPI is running"
    }


app.include_router(health_router)