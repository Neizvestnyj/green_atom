from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_storage


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
    response = await async_client.post("/api/v1/storage/storage/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == data["name"]
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_already_exist_storage(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Проверяем, что хранилище с указанным именем существует

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания хранилища в тестах.
    :return: None
    """

    data = {
        "name": "Test organisation",
        "location": "Москва",
        "capacity": {
            "Пластик": [0, 60],
        }
    }

    await create_storage(db_session,
                         name=data['name'],
                         location=data['location'],
                         capacity=data['capacity'],
                         )
    response = await async_client.post("/api/v1/storage/storage/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == f'Хранилище с именем {data["name"]} уже существует'


@pytest.mark.asyncio
async def test_creat_organisation_without_name(async_client: AsyncClient) -> None:
    """
    Функция тестирует создание нового хранилиза без имени.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "capacity": {
            "Пластик": [0, 60],
        }
    }
    response = await async_client.post("/api/v1/storage/storage/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    missing_name_error = next(
        (
            error
            for error in resp_data["detail"]
            if error["type"] == "missing" and "name" in error["loc"]
        ),
        None,
    )
    assert missing_name_error is not None
    assert missing_name_error["msg"] == "Field required"


@pytest.mark.asyncio
async def test_get_storages(async_client: AsyncClient) -> None:
    """
    Функция проверяет правильность работы эндпоинта для получения списка всех хранилищ.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.get("/api/v1/storage/storages/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_empty_storage(async_client: AsyncClient) -> None:
    """
    Функция проверяет, что если нет хранилища для удаления, возвращается ошибка с детализированным сообщением.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.delete(f"/api/v1/storage/1/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_json = response.json()
    assert response_json["detail"] == "Не найдено хранилища для удаления"


@pytest.mark.asyncio
@patch("storage_app.api.send_storage_deleted_event", autospec=True)
async def test_delete_all_organisations(mock_send_event: AsyncMock,
                                        async_client: AsyncClient,
                                        db_session: AsyncSession,
                                        ) -> None:
    """
    Функция создает организацию, а затем проверяет, что событие о ее удалении было отправлено после успешного удаления.

    :param mock_send_event: Мок-функция для отправки события об удалении всех организаций.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания организации в тестах.
    :return: None
    """

    data = {
        "name": "Test organisation",
        "location": "Москва",
        "capacity": {
            "Пластик": [0, 60],
        }
    }

    storage = await create_storage(db_session,
                                   name=data['name'],
                                   location=data['location'],
                                   capacity=data['capacity'],
                                   )
    response = await async_client.delete(f"/api/v1/storage/{storage.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Хранилище успешно удалено"
    mock_send_event.assert_called_once()
