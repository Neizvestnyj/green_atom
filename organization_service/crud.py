from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Organisation, StorageCopy, StorageDistanceCopy
from schemas import OrganisationCreate


async def create_organisation(db: AsyncSession, org: OrganisationCreate):
    db_org = Organisation(name=org.name, capacity=org.capacity)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org


async def get_all_organisations(db: AsyncSession):
    result = await db.execute(select(Organisation))
    return result.scalars().all()


# Метод для создания копии хранилища в сервисе Организации
async def create_storage_copy(db: AsyncSession, storage_id: int, capacity: dict):
    db_storage_copy = StorageCopy(id=storage_id, capacity=capacity)
    db.add(db_storage_copy)
    await db.commit()
    await db.refresh(db_storage_copy)
    return db_storage_copy


# Метод для создания копии записи о расстоянии между хранилищем и организацией
async def create_storage_distance_copy(db: AsyncSession, storage_distance_id: int, storage_id: int,
                                       organisation_id: int, distance: float):
    db_storage_distance_copy = StorageDistanceCopy(id=storage_distance_id,
                                                   storage_id=storage_id,
                                                   organisation_id=organisation_id,
                                                   distance=distance
                                                   )
    db.add(db_storage_distance_copy)
    await db.commit()
    await db.refresh(db_storage_distance_copy)
    return db_storage_distance_copy
