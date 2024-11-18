from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation, create_storage, create_distance


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
    response = await async_client.post("/api/v1/storage/distance/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["distance"] == data["distance"]
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_already_exist_storage_distance(async_client: AsyncClient,
                                                     db_session: AsyncSession,
                                                     ):
    """
    Проверяем, что не можем создать 2 одинаковых `StorageDistance`

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(db_session)
    storage = await create_storage(db_session,
                                   name='Тест МНО',
                                   location='Тверь',
                                   capacity={"Пластик": [0, 60]},
                                   )

    data = {"storage_id": storage.id, "organisation_id": organisation.id, "distance": 100}
    await create_distance(db_session, **data)
    response = await async_client.post("/api/v1/storage/distance/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == 'Такая запись уже существует'


@pytest.mark.asyncio
async def test_creat_storage_distance_without_organisation_id(async_client: AsyncClient) -> None:
    """
    Функция тестирует создание `StorageDistance` без указания `organisation_id`.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {"storage_id": 1, "distance": 100}

    response = await async_client.post("/api/v1/storage/distance/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    missing_organisation_id_error = next(
        (
            error
            for error in resp_data["detail"]
            if error["type"] == "missing" and "organisation_id" in error["loc"]
        ),
        None,
    )
    assert missing_organisation_id_error is not None
    assert missing_organisation_id_error["msg"] == "Field required"


@pytest.mark.asyncio
async def test_creat_storage_distance_without_organisation(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Функция тестирует создание `StorageDistance`, когда организации с указанным id в БД нет.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    storage = await create_storage(db_session,
                                   name='Тест МНО',
                                   location='Тверь',
                                   capacity={"Пластик": [0, 60]},
                                   )

    data = {"storage_id": storage.id, "organisation_id": 1, "distance": 100}

    response = await async_client.post("/api/v1/storage/distance/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == 'Указанной организации не существует'


@pytest.mark.asyncio
async def test_creat_storage_distance_without_storage(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Функция тестирует создание `StorageDistance`, когда хранилища с указанным id в БД нет.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    organisation = await create_organisation(db_session)

    data = {"storage_id": 1, "organisation_id": organisation.id, "distance": 100}

    response = await async_client.post("/api/v1/storage/distance/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == 'Указанного хранилища не существует'


@pytest.mark.asyncio
async def test_get_storage_distances(async_client: AsyncClient) -> None:
    """
    Функция проверяет правильность работы эндпоинта для получения списка всех `StorageDistance`.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.get("/api/v1/storage/distances/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_empty_distance(async_client: AsyncClient) -> None:
    """
    Функция проверяет, что если нет расстояния, возвращается ошибка.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.delete(f"/api/v1/storage/distance/1/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_json = response.json()
    assert response_json["detail"] == "Не найдено расстояние между МНО и ОО для удаления"


@pytest.mark.asyncio
@patch("storage_app.api.send_distance_deleted_event", autospec=True)
async def test_delete_distance(mock_send_event: AsyncMock,
                               async_client: AsyncClient,
                               db_session: AsyncSession,
                               ) -> None:
    """
    Проверяем успешное удаление расстояния

    :param mock_send_event: Мок-функция для отправки события об удалении всех организаций.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания организации в тестах.
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
    distance = await create_distance(db_session, **data)
    response = await async_client.delete(f"/api/v1/storage/distance/{distance.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Расстояние между ОО и МНО успешно удалено"
    mock_send_event.assert_called_once()
