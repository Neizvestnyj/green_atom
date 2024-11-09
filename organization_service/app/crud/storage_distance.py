from sqlalchemy.ext.asyncio import AsyncSession

from organization_service.app.models.storage_distance import StorageDistanceCopy


async def create_storage_distance_copy(
        db: AsyncSession,
        storage_distance_id: int,
        storage_id: int,
        organisation_id: int,
        distance: int,
) -> StorageDistanceCopy:
    """
    Создание копии записи о расстоянии между хранилищем и организацией.

    :param db: асинхронная сессия базы данных
    :param storage_distance_id: идентификатор записи о расстоянии
    :param storage_id: идентификатор хранилища
    :param organisation_id: идентификатор организации
    :param distance: расстояние между хранилищем и организацией
    :return: созданная копия записи о расстоянии
    """

    db_storage_distance_copy = StorageDistanceCopy(
        id=storage_distance_id,
        storage_id=storage_id,
        organisation_id=organisation_id,
        distance=distance,
    )

    db.add(db_storage_distance_copy)
    await db.commit()
    await db.refresh(db_storage_distance_copy)

    return db_storage_distance_copy
