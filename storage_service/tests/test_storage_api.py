from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@patch("storage_app.api.send_storage_created_event", autospec=True)
async def test_create_storage(mock_send_event: AsyncMock, async_client: AsyncClient) -> None:
    """
    Функция тестирует создание новой организации с заданными параметрами и проверяет,
    что событие о создании организации было отправлено.

    :param mock_send_event: Мок-функция для отправки события о создании хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "name": "Test organisation",
        "location": "Москва",
        "capacity": {
            "Пластик": [0, 60],
            "Стекло": [0, 20],
            "Биоотходы": [0, 50]
        }
    }
    response = await async_client.post("/api/storages/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == data["name"]
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_storages(async_client: AsyncClient) -> None:
    """
    Функция проверяет правильность работы эндпоинта для получения списка всех хранилищ.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.get("/api/storages/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
