from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__="users"
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=True)

    backups: Mapped[list["Backups"]] = relationship(back_populates="user")


class Backups(Base):
    __tablename__="backups"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    path: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["Users"] = relationship(back_populates="backups")


#class UserSettings(Base):
#    __tablename__="settings"