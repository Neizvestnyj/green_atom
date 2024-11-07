from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import StorageCopy, StorageDistanceCopy, Organisation
from schemas import OrganisationCreate


async def create_organisation(db: AsyncSession, org: OrganisationCreate) -> Organisation:
    """
    Создание новой организации в базе данных.

    :param db: асинхронная сессия базы данных
    :param org: данные для создания организации
    :return: созданная организация
    """

    db_org = Organisation(name=org.name, capacity=org.capacity)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)

    return db_org


async def get_all_organisations(db: AsyncSession) -> Sequence[Organisation]:
    """
    Получение всех организаций из базы данных.

    :param db: асинхронная сессия базы данных
    :return: список организаций
    """

    result = await db.execute(select(Organisation))

    return result.scalars().all()


async def create_storage_copy(db: AsyncSession, storage_id: int, capacity: dict) -> StorageCopy:
    """
    Создание копии хранилища.

    :param db: асинхронная сессия базы данных
    :param storage_id: идентификатор хранилища
    :param capacity: вместимость хранилища
    :return: созданная копия хранилища
    """

    db_storage_copy = StorageCopy(id=storage_id, capacity=capacity)
    db.add(db_storage_copy)
    await db.commit()
    await db.refresh(db_storage_copy)

    return db_storage_copy


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


async def delete_all_organisations(db: AsyncSession) -> Sequence[Organisation]:
    """
    Удаление всех организаций из базы данных.

    :param db: асинхронная сессия базы данных
    :return: список удаленных организаций
    """

    # Получаем все организации
    result = await db.execute(select(Organisation))
    organisations = result.scalars().all()

    if not organisations:
        return []

    # Удаляем все организации
    for organisation in organisations:
        await db.delete(organisation)
    await db.commit()

    return organisations
