import asyncio
from typing import Any, Dict, List, Tuple

import httpx

ORGANISATION_URL = "http://localhost/api/v1/organisation"  # :8000
STORAGE_URL = "http://localhost/api/v1/storage"  # :8001


async def create_organisation(
        client: httpx.AsyncClient,
        name: str,
        capacity: Dict[str, List[int]]
) -> Tuple[int, Dict[str, Any]]:
    """
    Создание организации.

    :param client: HTTP-клиент для выполнения запросов
    :param name: Название организации
    :param capacity: Емкость организации в формате {"тип отхода": [текущая емкость, максимальная емкость]}
    :return: Кортеж, содержащий статус-код и тело ответа
    """

    response = await client.post(
        f"{ORGANISATION_URL}/organisation/",
        json={"name": name, "capacity": capacity}
    )

    return response.status_code, response.json()


async def create_storage(
        client: httpx.AsyncClient,
        name: str,
        location: str,
        capacity: Dict[str, List[int]]
) -> Tuple[int, Dict[str, Any]]:
    """
    Создание склада.

    :param client: HTTP-клиент для выполнения запросов
    :param name: Название склада
    :param location: Местоположение склада
    :param capacity: Емкость склада в формате {"тип отхода": [текущая емкость, максимальная емкость]}
    :return: Кортеж, содержащий статус-код и тело ответа
    """

    response = await client.post(
        f"{STORAGE_URL}/storage/",
        json={"name": name, "location": location, "capacity": capacity}
    )

    return response.status_code, response.json()


async def create_storage_distance(
        client: httpx.AsyncClient,
        storage_id: int,
        organisation_id: int,
        distance: float
) -> Dict[str, Any]:
    """
    Создание расстояния между складом и организацией.

    :param client: HTTP-клиент для выполнения запросов
    :param storage_id: Идентификатор склада
    :param organisation_id: Идентификатор организации
    :param distance: Расстояние между складом и организацией
    :return: Ответ API в формате словаря
    """

    response = await client.post(
        f"{STORAGE_URL}/distance/",
        json={"storage_id": storage_id, "organisation_id": organisation_id, "distance": distance}
    )

    return response.json()


async def create_test_data() -> None:
    """
    Создание тестовых данных.

    :raises ValueError: Если создание организаций или складов завершилось с ошибкой
    """

    async with httpx.AsyncClient() as client:
        # Создание организаций
        oo1_capacity = {
            "Пластик": [10, 10],
            "Стекло": [50, 50],
            "Биоотходы": [50, 50]
        }

        oo2_capacity = {
            "Пластик": [60, 60],
            "Стекло": [20, 20],
            "Биоотходы": [50, 50]
        }

        oo1 = await create_organisation(client, "ОО1", oo1_capacity)
        oo2 = await create_organisation(client, "ОО2", oo2_capacity)

        if oo1[0] != 200 or oo2[0] != 200:
            raise ValueError(f"Организации не были созданы {oo1[1]}, {oo2[1]}")

        # Создание складов
        storage_capacities = {
            "МНО1": {"location": "Москва", "capacity": {"Стекло": [0, 300], "Пластик": [0, 100]}},
            "МНО2": {"location": "Москва", "capacity": {"Пластик": [0, 50], "Биоотходы": [0, 150]}},
            "МНО3": {"location": "Москва", "capacity": {"Пластик": [0, 10], "Биоотходы": [0, 250]}},
            "МНО5": {"location": "Москва", "capacity": {"Стекло": [0, 220], "Биоотходы": [0, 25]}},
            "МНО6": {"location": "Москва", "capacity": {"Стекло": [0, 100], "Биоотходы": [0, 150]}},
            "МНО7": {"location": "Москва", "capacity": {"Пластик": [0, 100], "Биоотходы": [0, 250]}},
            "МНО8": {"location": "Москва", "capacity": {"Стекло": [0, 35], "Пластик": [0, 25], "Биоотходы": [0, 52]}},
            "МНО9": {"location": "Москва", "capacity": {"Пластик": [0, 250], "Биоотходы": [0, 20]}},
        }

        storages = {}
        for name, details in storage_capacities.items():
            response = await create_storage(client, name, details["location"], details["capacity"])
            if response[0] != 200:
                raise ValueError(f'Хранилище {name} не было создано {response[1]}')
            storages[name] = response[1]

        # Создание расстояний
        await create_storage_distance(client, storages["МНО1"]["id"], oo1[1]["id"], 100)
        await create_storage_distance(client, storages["МНО2"]["id"], oo1[1]["id"], 50)
        await create_storage_distance(client, storages["МНО3"]["id"], oo1[1]["id"], 600)
        await create_storage_distance(client, storages["МНО5"]["id"], oo1[1]["id"], 100)
        await create_storage_distance(client, storages["МНО6"]["id"], oo1[1]["id"], 1200)
        await create_storage_distance(client, storages["МНО7"]["id"], oo1[1]["id"], 650)
        await create_storage_distance(client, storages["МНО8"]["id"], oo1[1]["id"], 600)
        await create_storage_distance(client, storages["МНО9"]["id"], oo1[1]["id"], 610)
        await create_storage_distance(client, storages["МНО3"]["id"], oo2[1]["id"], 50)
        await create_storage_distance(client, storages["МНО6"]["id"], oo2[1]["id"], 650)
        await create_storage_distance(client, storages["МНО7"]["id"], oo2[1]["id"], 100)


if __name__ == "__main__":
    asyncio.run(create_test_data())
