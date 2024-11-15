from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation, create_storage


@pytest.mark.asyncio
@patch("storage_app.api.send_storage_distance_created_event")
async def test_create_storage_distance(mock_send_event: AsyncMock,
                                       async_client: AsyncClient,
                                       db_session: AsyncSession,
                                       ):
    """
    Проверяется создание `StorageDistance`.

    :param mock_send_event: Мок-функция для отправки события о создании `StorageDistance`.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(db_session)
    storage = await create_storage(db_session,
                                   name='Тест МНО',
                                   location='Тверь',
                                   capacity={"Пластик": [0, 60],
                                             }
                                   )

    data = {"storage_id": storage.id, "organisation_id": organisation.id, "distance": 100}
    response = await async_client.post("/api/storage_distances/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["distance"] == data["distance"]
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_storage_distances(async_client: AsyncClient) -> None:
    """
    Функция проверяет правильность работы эндпоинта для получения списка всех `StorageDistance`.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.get("/api/storage_distances/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
