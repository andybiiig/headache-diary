"""Pydantic-схемы для аутентификации и регистрации."""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Схема для регистрации нового пользователя через веб-форму."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Схема для входа пользователя через веб-форму."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    """Схема JWT-токена, возвращаемого после успешного входа."""

    access_token: str
    token_type: str = "bearer"