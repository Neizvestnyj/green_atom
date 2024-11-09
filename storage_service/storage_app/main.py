from fastapi import FastAPI

from storage_app.api import router as storage_router
from storage_app.database import init_db
from storage_app.events.listen import start_listening_events

app = FastAPI()
app.include_router(storage_router, prefix="/api", tags=["storages"])


@app.on_event("startup")
async def startup() -> None:
    """
    Функция, которая выполняется при старте приложения.

    :return: None

    Инициализирует базу данных с помощью функции `init_db()` и запускает прослушивание событий,
    используя `start_listening_events()` для асинхронной обработки событий в отдельных потоках.
    """

    await init_db()  # Инициализация базы данных
    start_listening_events()  # Запуск прослушивания событий в отдельных потоках


if __name__ == "__main__":
    import uvicorn

    # Запуск приложения через uvicorn на порту 8001
    uvicorn.run('main:app', host="localhost", port=8001, reload=True, log_level='debug')
