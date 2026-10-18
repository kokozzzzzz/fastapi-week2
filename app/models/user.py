from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column

from app.db.base import Base


# 用户类包含：用户id，用户名，用户年龄
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        nullable=False
    )




