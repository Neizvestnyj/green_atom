from typing import Dict
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Organisation
from models import StorageDistanceCopy, StorageCopy
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


async def get_organisation(db: AsyncSession, organisation_id: int) -> Organisation:
    """
    Возвращает организацию по её ID.

    :param db: Асинхронная сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: Организация или None, если организация не найдена
    """

    result = await db.execute(select(Organisation).where(Organisation.id == organisation_id))
    return result.scalar_one_or_none()


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


async def get_storage_copy(db: AsyncSession, storage_id: int) -> StorageCopy:
    """
    Возвращает копию хранилища по ID.

    :param db: Асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :return: Копия хранилища или None, если копия не найдена
    """
    result = await db.execute(select(StorageCopy).where(StorageCopy.id == storage_id))

    return result.scalars().first()


# TODO: в отдельной папке services
async def find_nearest_storage(db: AsyncSession, organisation_id: int) -> Dict[int, Dict[str, int]]:
    # Получаем данные организации, включая её доступные объёмы отходов
    organisation = await get_organisation(db, organisation_id)
    if not organisation:
        raise ValueError("Organisation not found")

    storage_plan = {}
    organisation_capacity = organisation.capacity  # Например, {"Стекло": [0, 100], "Пластик": [0, 50]}

    # Получаем все записи расстояний, связанных с данной организацией
    storage_distances = await db.execute(
        select(StorageDistanceCopy).where(StorageDistanceCopy.organisation_id == organisation_id)
    )
    storage_distances = storage_distances.scalars().all()

    # Инициализация логики для распределения отходов
    for waste_type, (used, total) in organisation_capacity.items():
        remaining = total - used
        if remaining <= 0:
            continue

        # Сортируем хранилища по расстоянию от данной организации
        sorted_distances = sorted(storage_distances, key=lambda x: x.distance)

        for distance in sorted_distances:
            storage_id = distance.storage_id

            # Проверяем, достаточно ли места для данного вида отхода в хранилище
            storage_copy = await get_storage_copy(db, storage_id)
            if not storage_copy:
                continue

            # Проверка вместимости для текущего вида отходов
            if waste_type in storage_copy.capacity:
                storage_capacity_left = storage_copy.capacity[waste_type][1] - storage_copy.capacity[waste_type][0]
                if storage_capacity_left > 0:
                    amount_to_store = min(remaining, storage_capacity_left)

                    # Обновляем план распределения
                    if storage_id not in storage_plan:
                        storage_plan[storage_id] = {}
                    storage_plan[storage_id][waste_type] = amount_to_store

                    remaining -= amount_to_store

                    # Если все отходы данного типа распределены, переходим к следующему
                    if remaining <= 0:
                        break

    return storage_plan
