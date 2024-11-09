from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import get_organisation
from org_app.crud.storage import get_storage_copy
from org_app.models.storage_distance import StorageDistanceCopy


async def find_nearest_storage(db: AsyncSession, organisation_id: int) -> Dict[int, Dict[str, int]]:
    """
     Найти ближайшие хранилища для утилизации отходов организации.

     Функция принимает идентификатор организации, получает данные об отходах, которые она
     может утилизировать, и находит ближайшие хранилища, которые могут принять эти отходы.
     Функция возвращает план распределения отходов по хранилищам.

     :param db: Асинхронная сессия базы данных, используемая для выполнения запросов.
     :param organisation_id: Идентификатор организации, для которой нужно найти ближайшие хранилища.

     :return: Словарь, в котором ключ - это идентификатор хранилища, а значение - словарь типов отходов
              и объемов, которые могут быть распределены в данное хранилище.
              Пример:
              {
                  1: {"Стекло": 50, "Биоотходы": 100},
                  2: {"Стекло": 50}
              }

     :raises ValueError: Если организация с указанным идентификатором не найдена в базе данных.
     """

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
