from sqlalchemy import create_engine

from app.core.config import setting
from sqlalchemy.orm import sessionmaker

# 引擎
engine = create_engine(
    setting.database_url
)


SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()






