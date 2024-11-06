from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from storage_service.models import OrganisationCopy


async def create_storage(db: AsyncSession, storage: schemas.StorageCreate):
    db_storage = models.Storage(name=storage.name, location=storage.location, capacity=storage.capacity)
    db.add(db_storage)
    await db.commit()
    await db.refresh(db_storage)
    return db_storage


async def create_storage_distance(db: AsyncSession, distance: schemas.StorageDistanceBase):
    db_distance = models.StorageDistance(
        storage_id=distance.storage_id,
        organisation_id=distance.organisation_id,
        distance=distance.distance
    )

    db.add(db_distance)
    await db.commit()
    await db.refresh(db_distance)
    return db_distance


async def create_organisation_copy(db: AsyncSession, organisation_id: int):
    db_org_copy = models.OrganisationCopy(id=organisation_id)
    db.add(db_org_copy)
    await db.commit()


async def delete_organisation_by_id(db: AsyncSession, organisation_id: int):
    """Удаляем организацию по ID, используя каскадное удаление для связанных записей."""
    result = await db.execute(select(OrganisationCopy).filter(OrganisationCopy.id == organisation_id))
    organisation = result.scalars().first()

    if organisation:
        await db.delete(organisation)
        await db.commit()


async def get_all_storages(db: AsyncSession):
    result = await db.execute(select(models.Storage))
    return result.scalars().all()


async def get_all_storage_distances(db: AsyncSession):
    result = await db.execute(select(models.StorageDistance))
    return result.scalars().all()
