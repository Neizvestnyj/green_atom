from fastapi import FastAPI

import database
from api import router as organisations_router
from events import start_listening_events

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

    await database.init_db()  # Инициализация базы данных
    start_listening_events()  # Запуск прослушивания событий в отдельных потоках


if __name__ == "__main__":
    import uvicorn

    # Запуск приложения через uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True, log_level='debug')
