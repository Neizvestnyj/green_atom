from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import get_organisation
from org_app.crud.storage import get_storage_copy
from org_app.models.storage_distance import StorageDistanceCopy


async def find_nearest_storage(db: AsyncSession, organisation_id: int) -> tuple[
    Dict[int, Dict[str, int]], Dict[str, int], Dict[str, int]]:
    """
    Функция позволяет найти ближайшие хранилища для утилизации отходов организации и вернуть информацию о переработанных отходах.

    :param db: Асинхронная сессия базы данных, используемая для выполнения запросов.
    :param organisation_id: Идентификатор организации, для которой нужно найти ближайшие хранилища.
    :return: Словарь с распределением отходов, общий объем переработанных отходов и остатки отходов, которые не поместились.
    """

    # Получаем данные организации, включая её доступные объёмы отходов
    organisation = await get_organisation(db, organisation_id)
    if not organisation:
        raise ValueError("Organisation not found")

    storage_plan = {}
    total_sent_waste = {}
    remaining_waste = {}  # Словарь для отслеживания непоместившихся отходов
    organisation_capacity = organisation.capacity

    # Получаем все записи расстояний, связанных с данной организацией
    storage_distances = await db.execute(
        select(StorageDistanceCopy).where(StorageDistanceCopy.organisation_id == organisation_id)
    )
    storage_distances = storage_distances.scalars().all()

    for waste_type, (used, total) in organisation_capacity.items():
        remaining = total - used
        if remaining <= 0:
            continue

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

                    # Обновляем план хранения
                    if storage_id not in storage_plan:
                        storage_plan[storage_id] = {}
                    storage_plan[storage_id][waste_type] = amount_to_store

                    # Обновляем общий объем переработанных отходов
                    if waste_type not in total_sent_waste:
                        total_sent_waste[waste_type] = 0
                    total_sent_waste[waste_type] += amount_to_store

                    remaining -= amount_to_store

                    if remaining <= 0:
                        break

        # Если после всех попыток распределить отходы остался остаток, добавляем его в словарь remaining_waste
        if remaining > 0:
            remaining_waste[waste_type] = remaining

    return storage_plan, total_sent_waste, remaining_waste
