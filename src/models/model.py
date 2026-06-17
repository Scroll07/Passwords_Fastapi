from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func

from src.schemas.jwt import TokenType
from src.schemas.db_schema import UserRoles


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True) ,default=lambda: datetime.now(timezone.utc))

    backups: Mapped[list["Backups"]] = relationship(back_populates="user")



class Roles(Base):
    __tablename__="roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[UserRoles]

class Sessions(Base):
    __tablename__="sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
        
class Backups(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pinned: Mapped[bool] = mapped_column(default=False)                # Добавить pinned: bool
    name: Mapped[str] = mapped_column() #заменить на name
    rows: Mapped[int] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True) ,default=lambda: datetime.now(timezone.utc))

    user: Mapped["Users"] = relationship(back_populates="backups")
        
# class UserSettings(Base):
#    __tablename__="settings"
