from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from storage_app.api import router as storage_router
from storage_app.database import init_db
from storage_app.events.consumers import start_listening_events


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Функция, которая выполняется при старте приложения и завершении.

    :return: None

    Инициализирует базу данных с помощью функции `init_db()` и запускает прослушивание событий,
    используя `start_listening_events()`.
    """

    # код инициализации
    await init_db()  # Инициализация базы данных
    start_listening_events()  # Запуск прослушивания событий в отдельных потоках
    yield
    # код завершения работы


app = FastAPI(lifespan=lifespan)
app.include_router(storage_router, prefix="/api/v1/storage", tags=["storages"])

if __name__ == "__main__":
    import uvicorn

    # Запуск приложения через uvicorn на порту 8001
    uvicorn.run('main:app', host="localhost", port=8001, reload=True, log_level='debug')
