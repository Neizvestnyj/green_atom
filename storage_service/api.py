from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import AsyncSessionLocal
from events import send_storage_created_event, send_storage_distance_created_event

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/storages/", response_model=schemas.Storage)
async def create_storage(storage: schemas.StorageCreate, db: AsyncSession = Depends(get_db)):
    db_storage = await crud.create_storage(db, storage)
    send_storage_created_event(db_storage)
    return db_storage


@router.post("/storage_distances/", response_model=schemas.StorageDistance)
async def create_storage_distance(distance: schemas.StorageDistanceBase, db: AsyncSession = Depends(get_db)):
    db_distance = await crud.create_storage_distance(db, distance)
    send_storage_distance_created_event(db_distance)
    return db_distance


@router.get("/storages/", response_model=list[schemas.Storage])
async def get_storages(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_storages(db)


@router.get("/storage_distances/", response_model=list[schemas.StorageDistance])
async def get_storage_distances(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_storage_distances(db)
