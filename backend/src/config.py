from functools import lru_cache
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Вычисляем базовый путь к папке backend/ относительно текущего файла config.py
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Строка асинхронного подключения к Postgres
    database_url: str

    # Настройки JWT безопасности
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 часа (60 минут * 24)

    # ЕДИНСТВЕННЫЙ верный способ конфигурации для Pydantic v2
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать сторонние переменные в .env
        case_sensitive=False,  # Игнорировать регистр (DATABASE_URL сопоставится с database_url)
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Экспортируем синглтон для удобного импорта в роутерах
settings = get_settings()