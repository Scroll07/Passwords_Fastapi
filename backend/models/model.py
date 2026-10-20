from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, LargeBinary, func, text

from backend.schemas.db_schema import (
    UserRoles,
    SessionType
)


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int | None] = mapped_column(unique=True, nullable=True, server_default=text("Null"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    is_active: Mapped[bool] = mapped_column(server_default=text("True"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    backups: Mapped[list["Backups"]] = relationship(back_populates="user")

class Roles(Base):
    __tablename__="roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[UserRoles]

class Sessions(Base):
    __tablename__="sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    vault_id: Mapped[int | None] = mapped_column(ForeignKey("vaults.id", ondelete="CASCADE"), nullable=True)
    type: Mapped[SessionType] = mapped_column(nullable=False) 
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(server_default=text("True"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
        
class Backups(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pinned: Mapped[bool] = mapped_column(server_default=text("False"))
    name: Mapped[str] = mapped_column(nullable=False)
    rows: Mapped[int] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["Users"] = relationship(back_populates="backups")
        
class Vaults(Base):
    __tablename__ = "vaults"
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)       
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pinned: Mapped[bool] = mapped_column(server_default=text("False"))
    name: Mapped[str] = mapped_column(nullable=False)
    entries: Mapped[int] = mapped_column(server_default=text("0"))
    encrypted_passwords: Mapped[str] = mapped_column(nullable=False)
    salt: Mapped[str] = mapped_column(nullable=False)
    encrypted_dek: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())



# class UserSettings(Base):
#    __tablename__="settings"
