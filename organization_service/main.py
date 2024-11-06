from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import database
import schemas
from database import AsyncSessionLocal
from events import send_organisation_created_event, start_listening_events

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.init_db()
    start_listening_events()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/organisations/", response_model=schemas.Organisation)
async def create_organisation(org: schemas.OrganisationCreate, db: AsyncSession = Depends(get_db)):
    organisation = await crud.create_organisation(db, org)
    send_organisation_created_event(organisation)
    return organisation


@app.get("/organisations/", response_model=list[schemas.Organisation])
async def get_organisations(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_organisations(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
