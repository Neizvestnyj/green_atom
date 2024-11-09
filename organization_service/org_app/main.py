from fastapi import FastAPI

from org_app.api import router as organisations_router
from org_app.database import init_db
from org_app.events.listen import start_listening_events

app = FastAPI()
app.include_router(organisations_router, prefix="/api", tags=["organisations"])


@app.on_event("startup")
async def startup() -> None:
    """
    Функция, которая выполняется при старте приложения.

    :return: None

    Инициализирует базу данных с помощью функции `init_db()` и запускает прослушивание событий,
    используя `start_listening_events()`.
    """

    await init_db()  # Инициализация базы данных
    start_listening_events()  # Запуск прослушивания событий в отдельных потоках


if __name__ == "__main__":
    import uvicorn

    # Запуск приложения через uvicorn
    uvicorn.run('main:app', host="localhost", port=8000, reload=True, log_level='debug')
