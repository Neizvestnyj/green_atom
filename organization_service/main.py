from fastapi import FastAPI

import database
from api import router as organisations_router
from events import start_listening_events

app = FastAPI()
app.include_router(organisations_router, prefix="/api", tags=["organisations"])


@app.on_event("startup")
async def startup():
    await database.init_db()
    start_listening_events()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True, log_level='debug')
