from sqlalchemy.ext.asyncio import AsyncSession

from org_app.models.storage_distance import StorageDistanceCopy
from org_app.schemas.storage_distance import StorageDistanceCopySchema


async def create_storage_distance_copy(
        db: AsyncSession,
        storage_distance: StorageDistanceCopySchema,
) -> StorageDistanceCopy:
    """
    Создание копии записи о расстоянии между хранилищем и организацией.

    :param db: асинхронная сессия базы данных
    :param storage_distance: данные для создания `StorageDistanceCopy`
    :return: созданная копия записи о расстоянии
    """

    db_storage_distance_copy = StorageDistanceCopy(
        id=storage_distance.id,
        storage_id=storage_distance.storage_id,
        organisation_id=storage_distance.organisation_id,
        distance=storage_distance.distance,
    )

    db.add(db_storage_distance_copy)
    await db.commit()
    await db.refresh(db_storage_distance_copy)

    return db_storage_distance_copy
