"""Модель пользователя."""

import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from database import Base

if TYPE_CHECKING:
    from models.diary import Attack


class Gender(str, Enum):
    """Пол пользователя."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


def _utc_now() -> datetime:
    """Возвращает текущее время в UTC без информации о часовом поясе."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Пользователь системы (веб или Telegram)."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR telegram_id IS NOT NULL",
            name="ck_users_email_or_telegram_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str | None] = mapped_column(
        String(320),
        unique=True,
        nullable=True,
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
    )
    role: Mapped[str] = mapped_column(String(32), default="client", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        SQLEnum(Gender, name="gender_enum", native_enum=False),
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        default="Europe/Moscow",
        nullable=False,
    )
    is_banned_from_commenting: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=_utc_now,
        nullable=False,
    )

    attacks: Mapped[list["Attack"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
