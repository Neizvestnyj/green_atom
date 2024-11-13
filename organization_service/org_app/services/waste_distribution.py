from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import get_organisation
from org_app.crud.storage import get_storage_copy
from org_app.models.storage_distance import StorageDistanceCopy


async def find_nearest_storage(db: AsyncSession, organisation_id: int) -> tuple[
    Dict[int, Dict[str, int]], Dict[str, int], bool]:
    """
    Найти ближайшие хранилища для утилизации отходов организации и вернуть информацию о переработанных отходах.

    Функция принимает идентификатор организации, получает данные об отходах, которые она
    может утилизировать, и находит ближайшие хранилища, которые могут принять эти отходы.
    Функция возвращает план распределения отходов по хранилищам и общий объем переработанных отходов.

    :param db: Асинхронная сессия базы данных, используемая для выполнения запросов.
    :param organisation_id: Идентификатор организации, для которой нужно найти ближайшие хранилища.

    :return: Словарь с распределением отходов, общий объем переработанных отходов и флаг, указывающий, переработаны ли все отходы.
    {
        3: {'Пластик': 10, 'Биоотходы': 50},
        6: {'Пластик': 50},
        5: {'Стекло': 20}
    },
    {'Пластик': 60, 'Стекло': 20, 'Биоотходы': 50},
    False
    """

    # Получаем данные организации, включая её доступные объёмы отходов
    organisation = await get_organisation(db, organisation_id)
    if not organisation:
        raise ValueError("Organisation not found")

    storage_plan = {}
    total_sent_waste = {}
    organisation_capacity = organisation.capacity

    # Проверяем, все ли отходы уже переработаны
    all_waste_processed = True  # Переменная для проверки переработки всех отходов

    # Получаем все записи расстояний, связанных с данной организацией
    storage_distances = await db.execute(
        select(StorageDistanceCopy).where(StorageDistanceCopy.organisation_id == organisation_id)
    )
    storage_distances = storage_distances.scalars().all()

    for waste_type, (used, total) in organisation_capacity.items():
        remaining = total - used
        if remaining <= 0:
            continue

        all_waste_processed = False  # Если хотя бы один тип отходов не переработан, меняем флаг

        # Сортируем хранилища по расстоянию от данной организации
        sorted_distances = sorted(storage_distances, key=lambda x: x.distance)

        for distance in sorted_distances:
            storage_id = distance.storage_id

            storage_copy = await get_storage_copy(db, storage_id)
            if not storage_copy:
                continue

            if waste_type in storage_copy.capacity:
                storage_capacity_left = storage_copy.capacity[waste_type][1] - storage_copy.capacity[waste_type][0]
                if storage_capacity_left > 0:
                    amount_to_store = min(remaining, storage_capacity_left)

                    if storage_id not in storage_plan:
                        storage_plan[storage_id] = {}
                    storage_plan[storage_id][waste_type] = amount_to_store

                    if waste_type not in total_sent_waste:
                        total_sent_waste[waste_type] = 0
                    total_sent_waste[waste_type] += amount_to_store

                    remaining -= amount_to_store

                    if remaining <= 0:
                        break

    return storage_plan, total_sent_waste, all_waste_processed
