from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from storage_service.models import OrganisationCopy


async def create_storage(db: AsyncSession, storage: schemas.StorageCreate) -> models.Storage:
    """
    Создание нового хранилища.

    :param db: Сессия базы данных
    :param storage: Данные для создания хранилища
    :return: Созданное хранилище

    Создает новое хранилище в базе данных и возвращает созданную запись.
    """

    db_storage = models.Storage(name=storage.name, location=storage.location, capacity=storage.capacity)
    db.add(db_storage)
    await db.commit()
    await db.refresh(db_storage)

    return db_storage


async def create_storage_distance(db: AsyncSession, distance: schemas.StorageDistanceBase) -> models.StorageDistance:
    """
    Создание новой записи о расстоянии между хранилищем и организацией.

    :param db: Сессия базы данных
    :param distance: Данные для создания записи о расстоянии
    :return: Созданная запись о расстоянии

    Создает запись о расстоянии и возвращает её.
    """

    db_distance = models.StorageDistance(
        storage_id=distance.storage_id,
        organisation_id=distance.organisation_id,
        distance=distance.distance
    )

    db.add(db_distance)
    await db.commit()
    await db.refresh(db_distance)

    return db_distance


async def create_organisation_copy(db: AsyncSession, organisation_id: int) -> None:
    """
    Создание копии записи об организации.

    :param db: Сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: None

    Создает копию организации в базе данных.
    """

    db_org_copy = models.OrganisationCopy(id=organisation_id)
    db.add(db_org_copy)
    await db.commit()


async def delete_organisation_by_id(db: AsyncSession, organisation_id: int) -> None:
    """
    Удаление организации по ID.

    :param db: Сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: None

    Удаляет организацию и её связанные записи с помощью каскадного удаления.
    """

    result = await db.execute(select(OrganisationCopy).filter(OrganisationCopy.id == organisation_id))
    organisation = result.scalars().first()

    if organisation:
        await db.delete(organisation)
        await db.commit()


async def get_all_storages(db: AsyncSession) -> list[models.Storage]:
    """
    Получение всех хранилищ.

    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает список всех хранилищ в базе данных.
    """

    result = await db.execute(select(models.Storage))

    return list(result.scalars().all())


async def get_all_storage_distances(db: AsyncSession) -> list[models.StorageDistance]:
    """
    Получение всех записей о расстояниях между хранилищами и организациями.

    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает список всех записей о расстояниях.
    """

    result = await db.execute(select(models.StorageDistance))

    return list(result.scalars().all())
