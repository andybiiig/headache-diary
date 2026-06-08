"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI
from routes.auth import router as auth_router

app = FastAPI(title="Headache Diary")

app.include_router(auth_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверка доступности сервиса."""
    return {"status": "ok"}
