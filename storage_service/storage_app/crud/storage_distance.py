from typing import Sequence, Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from storage_app.models.organisation import OrganisationCopy
from storage_app.models.storage import Storage
from storage_app.models.storage_distance import StorageDistance
from storage_app.schemas.storage_distance import StorageDistanceBaseSchema


async def create_storage_distance(db: AsyncSession, distance: StorageDistanceBaseSchema) -> StorageDistance:
    """
    Создание новой записи о расстоянии между хранилищем и организацией.

    :param db: Сессия базы данных
    :param distance: Данные для создания записи о расстоянии
    :return: Созданная запись о расстоянии

    Создает запись о расстоянии и возвращает её.
    """

    existing_distance = await db.execute(
        select(StorageDistance).where(
            StorageDistance.storage_id == distance.storage_id,
            StorageDistance.organisation_id == distance.organisation_id,
            StorageDistance.distance == distance.distance
        )
    )
    if existing_distance.scalar():
        raise HTTPException(
            status_code=400,
            detail="Такая запись уже существует"
        )

    # Проверка существования storage_id
    storage_exists = await db.execute(select(Storage.id).where(Storage.id == distance.storage_id))
    if not storage_exists.scalar():
        raise HTTPException(status_code=400, detail="Указанного хранилища не существует")

    # Проверка существования organisation_id
    organisation_exists = await db.execute(
        select(OrganisationCopy.id).where(OrganisationCopy.id == distance.organisation_id))
    if not organisation_exists.scalar():
        raise HTTPException(status_code=400, detail="Указанной организации не существует")

    db_distance = StorageDistance(
        storage_id=distance.storage_id,
        organisation_id=distance.organisation_id,
        distance=distance.distance
    )

    db.add(db_distance)
    await db.commit()
    await db.refresh(db_distance)

    return db_distance


async def delete_distance(db: AsyncSession, distance_id: int) -> Union[StorageDistance, None]:
    """
    Удаление `StorageDistance`.

    :param db: асинхронная сессия базы данных
    :param distance_id: Идентификатор хранилища
    :return: список удаленных организаций
    """

    # Получаем все организации
    result = await db.execute(select(StorageDistance).filter_by(id=distance_id))
    distance = result.scalars().first()

    if not distance:
        return None

    await db.delete(distance)
    await db.commit()

    return distance


async def get_all_storage_distances(db: AsyncSession) -> Sequence[StorageDistance]:
    """
    Получение всех записей о расстояниях между хранилищами и организациями.

    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает список всех записей о расстояниях.
    """

    result = await db.execute(select(StorageDistance))

    return result.scalars().all()
