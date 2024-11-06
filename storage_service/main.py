from fastapi import FastAPI

import database
from api import router as storage_router
from events import start_listening_events

app = FastAPI()
app.include_router(storage_router, prefix="/api", tags=["storages"])


@app.on_event("startup")
async def startup():
    await database.init_db()
    start_listening_events()  # Запуск слушателей событий в отдельных потоках


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('main:app', host="127.0.0.1", port=8001, reload=True, log_level='debug')
