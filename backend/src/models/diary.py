"""Модели дневника: приступы и приём лекарств."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.user import User


def _utc_now() -> datetime:
    """Возвращает текущее время в UTC без информации о часовом поясе."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Attack(Base):
    """Запись о приступе головной боли."""

    __tablename__ = "attacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=_utc_now,
        nullable=False,
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pain_intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    pain_characteristics: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    localization_zone: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=_utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="attacks")
    medication_intakes: Mapped[list["MedicationIntake"]] = relationship(
        back_populates="attack",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MedicationIntake(Base):
    """Запись о принятом лекарстве во время приступа."""

    __tablename__ = "medication_intakes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    attack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attacks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(64), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=_utc_now,
        nullable=False,
    )

    attack: Mapped["Attack"] = relationship(back_populates="medication_intakes")
