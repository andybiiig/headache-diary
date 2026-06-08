"""Асинхронное подключение к PostgreSQL и фабрика сессий SQLAlchemy."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовый класс для ORM-моделей."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор сессий для dependency injection в FastAPI."""
    async with async_session_factory() as session:
        yield session
