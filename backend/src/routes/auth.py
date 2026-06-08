"""Роутер для аутентификации и регистрации пользователей (веб-форма)."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database import get_db
from models.user import User
from schemas.auth import Token, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


_REGISTER_WARNING = (
    "Если вы ранее регистрировались через Telegram-бота, не регистрируйтесь заново — "
    "войдите через бота или обратитесь в поддержку для связки аккаунтов."
)


def _hash_password(plain: str) -> str:
    """Хеширует пароль через нативный bcrypt."""
    # Переводим строку в байты, генерируем соль и хэшируем
    password_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def _verify_password(plain: str, hashed: str) -> bool:
    """Проверяет соответствие пароля хешу через нативный bcrypt."""
    try:
        password_bytes = plain.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def _create_access_token(
    data: dict[str, Any],
    settings: Settings,
) -> str:
    """Генерирует подписанный JWT access-токен."""
    from datetime import datetime, timezone

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация через веб-форму",
)
async def register(
    body: UserRegister,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """
    Регистрирует нового пользователя по email и паролю.

    - Проверяет уникальность email.
    - Хеширует пароль через bcrypt.
    - telegram_id, birth_date, gender остаются NULL.
    - timezone выставляется по умолчанию (Europe/Moscow).
    """
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует.",
        )

    user = User(
        email=body.email,
        password_hash=_hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        },
        "warning": _REGISTER_WARNING,
    }


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    summary="Вход через веб-форму",
)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    """
    Аутентифицирует пользователя по email и паролю, возвращает JWT.

    - Отдаёт одинаковую ошибку при неверном email и пароле
      (защита от перебора/энумерации).
    - Проверяет is_active: удалённые/заблокированные аккаунты не пускает.
    """
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    result = await db.execute(select(User).where(User.email == body.email))
    user: User | None = result.scalar_one_or_none()

    if user is None or not _verify_password(body.password, user.password_hash or ""):
        raise invalid_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован. Войдите снова, чтобы восстановить его.",
        )

    token = _create_access_token(
        data={"sub": str(user.id), "role": user.role},
        settings=settings,
    )
    return Token(access_token=token)