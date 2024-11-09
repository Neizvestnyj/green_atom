from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from storage_service.app.models.storage_distance import StorageDistance
from storage_service.app.schemas.storage_distance import StorageDistanceBaseSchema


async def create_storage_distance(db: AsyncSession, distance: StorageDistanceBaseSchema) -> StorageDistance:
    """
    Создание новой записи о расстоянии между хранилищем и организацией.

    :param db: Сессия базы данных
    :param distance: Данные для создания записи о расстоянии
    :return: Созданная запись о расстоянии

    Создает запись о расстоянии и возвращает её.
    """

    db_distance = StorageDistance(
        storage_id=distance.storage_id,
        organisation_id=distance.organisation_id,
        distance=distance.distance
    )

    db.add(db_distance)
    await db.commit()
    await db.refresh(db_distance)

    return db_distance


async def get_all_storage_distances(db: AsyncSession) -> Sequence[StorageDistance]:
    """
    Получение всех записей о расстояниях между хранилищами и организациями.

    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает список всех записей о расстояниях.
    """

    result = await db.execute(select(StorageDistance))

    return result.scalars().all()
