import asyncio

import httpx

ORGANISATION_URL = "http://localhost:8000/api"
STORAGE_URL = "http://localhost:8001/api"


# Функция для создания организации с capacity
async def create_organisation(client, name, capacity: dict):
    response = await client.post(f"{ORGANISATION_URL}/organisations/", json={"name": name, "capacity": capacity})
    return response.json()


# Функция для создания склада с capacity
async def create_storage(client, name, location, capacity: dict):
    response = await client.post(f"{STORAGE_URL}/storages/", json={
        "name": name,
        "location": location,
        "capacity": capacity
    })
    return response.json()


# Функция для создания расстояния между складами и организациями
async def create_storage_distance(client, storage_id, organisation_id, distance):
    response = await client.post(f"{STORAGE_URL}/storage_distances/", json={
        "storage_id": storage_id,
        "organisation_id": organisation_id,
        "distance": distance
    })
    return response.json()


# Функция для создания тестовых данных
async def create_test_data():
    async with httpx.AsyncClient() as client:
        # Создаем организации с соответствующими данными о capacity
        oo1_capacity = {
            "Пластик": [0, 10],
            "Стекло": [0, 50],
            "Биоотходы": [0, 50]
        }
        oo2_capacity = {
            "Пластик": [0, 60],
            "Стекло": [0, 20],
            "Биоотходы": [0, 50]
        }

        oo1 = await create_organisation(client, "ОО1", oo1_capacity)
        oo2 = await create_organisation(client, "ОО2", oo2_capacity)

        # Создаем склады с соответствующими данными о capacity
        mno1_capacity = {
            "Стекло": [0, 300],
            "Пластик": [0, 100]
        }
        mno2_capacity = {
            "Пластик": [0, 50],
            "Биоотходы": [0, 150]
        }
        mno3_capacity = {
            "Пластик": [0, 10],
            "Биоотходы": [0, 250]
        }
        mno5_capacity = {
            "Стекло": [0, 220],
            "Биоотходы": [0, 25]
        }
        mno6_capacity = {
            "Стекло": [0, 100],
            "Биоотходы": [0, 150]
        }
        mno7_capacity = {
            "Пластик": [0, 100],
            "Биоотходы": [0, 250]
        }
        mno8_capacity = {
            "Стекло": [0, 35],
            "Пластик": [0, 25],
            "Биоотходы": [0, 52]
        }
        mno9_capacity = {
            "Пластик": [0, 250],
            "Биоотходы": [0, 20]
        }

        mno1 = await create_storage(client, "МНО1", "Москва", mno1_capacity)
        mno2 = await create_storage(client, "МНО2", "Москва", mno2_capacity)
        mno3 = await create_storage(client, "МНО3", "Москва", mno3_capacity)
        mno5 = await create_storage(client, "МНО5", "Москва", mno5_capacity)
        mno6 = await create_storage(client, "МНО6", "Москва", mno6_capacity)
        mno7 = await create_storage(client, "МНО7", "Москва", mno7_capacity)
        mno8 = await create_storage(client, "МНО8", "Москва", mno8_capacity)
        mno9 = await create_storage(client, "МНО9", "Москва", mno9_capacity)

        # Создаем расстояния между складами и организациями
        # ОО1
        await create_storage_distance(client, mno1["id"], oo1["id"], 100)
        await create_storage_distance(client, mno2["id"], oo1["id"], 50)
        await create_storage_distance(client, mno3["id"], oo1["id"], 600)

        await create_storage_distance(client, mno5["id"], oo1["id"], 100)
        await create_storage_distance(client, mno6["id"], oo1["id"], 1200)
        await create_storage_distance(client, mno7["id"], oo1["id"], 650)
        await create_storage_distance(client, mno8["id"], oo1["id"], 600)
        await create_storage_distance(client, mno9["id"], oo1["id"], 610)

        # ОО2
        await create_storage_distance(client, mno3["id"], oo2["id"], 50)
        await create_storage_distance(client, mno6["id"], oo2["id"], 650)
        await create_storage_distance(client, mno7["id"], oo2["id"], 100)

        # Двусторонние связи


# Запускаем асинхронный скрипт для создания тестовых данных
asyncio.run(create_test_data())
