from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation


############################# CREATE ###################################

@pytest.mark.asyncio
@patch("org_app.api.send_organisation_created_event", autospec=True)
async def test_create_organisation(mock_send_event: AsyncMock, async_client: AsyncClient) -> None:
    """
    Функция тестирует создание новой организации с заданными параметрами и проверяет,
    что событие о создании организации было отправлено.

    :param mock_send_event: Мок-функция для отправки события о создании организации.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "name": "Test organisation",
        "capacity": {
            "Пластик": [60, 60],
            "Стекло": [20, 20],
            "Биоотходы": [50, 50]
        }
    }
    response = await async_client.post("/api/v1/organisation/organisation/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert resp_data["name"] == data["name"]
    assert resp_data["capacity"] == data["capacity"]
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_already_exist_organisation(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Проверяем, что организация с указанным именем существует

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания организации в тестах.
    :return: None
    """

    data = {
        "name": "Test organisation",
        "capacity": {
            "Пластик": [60, 60],
        }
    }
    await create_organisation(db_session,
                              name=data['name'],
                              capacity=data['capacity'],
                              )
    response = await async_client.post("/api/v1/organisation/organisation/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == f'Организация с именем {data["name"]} уже существует'


@pytest.mark.asyncio
async def test_creat_organisation_without_name(async_client: AsyncClient) -> None:
    """
    Функция тестирует создание новой организации без имени.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "capacity": {
            "Пластик": [60, 60],
        }
    }
    response = await async_client.post("/api/v1/organisation/organisation/", json=data)
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
async def test_creat_organisation_with_incorrect_name_type(async_client: AsyncClient) -> None:
    """
    Функция тестирует что тип name неверен.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "capacity": {
            "name": 123,
            "Пластик": [60, 60],
        }
    }
    response = await async_client.post("/api/v1/organisation/organisation/", json=data)
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
@patch("org_app.api.send_organisation_created_event", autospec=True)
async def test_creat_organisation_with_overflow_capacity(mock_send_event: AsyncMock, async_client: AsyncClient) -> None:
    """
    Проверяем, что не можем создать организацию с переполненной вместимостью

    :param mock_send_event: Мок-функция для отправки события о создании организации.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    data = {
        "name": "Тест ОО",
        "capacity": {
            "Пластик": [70, 60],
        }
    }
    response = await async_client.post("/api/v1/organisation/organisation/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_data["detail"] == "Переполнение для отхода Пластик: 70 превышает вместимость 60"
    mock_send_event.assert_not_called()


############################# GET ###################################

@pytest.mark.asyncio
async def test_get_organisations(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Функция проверяет правильность работы эндпоинта для получения списка всех организаций.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания организации в тестах.
    :return: None
    """

    await create_organisation(db_session,
                              name="New Test Organisation",
                              capacity={
                                  "Пластик": [50, 50],
                              },
                              )

    response = await async_client.get("/api/v1/organisation/organisations/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


############################# DELETE ###################################

@pytest.mark.asyncio
async def test_delete_empty_organisations(async_client: AsyncClient) -> None:
    """
    Функция проверяет, что если нет организаций для удаления, возвращается ошибка с детализированным сообщением.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.delete(f"/api/v1/organisation/organisation/1/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_json = response.json()
    assert response_json["detail"] == "Не найдено организации для удаления"


@pytest.mark.asyncio
@patch("org_app.api.send_organisation_delete_event", autospec=True)
async def test_delete_organisation(mock_send_event: AsyncMock,
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

    org = await create_organisation(db_session,
                                    name="New Test Organisation",
                                    capacity={
                                        "Пластик": [50, 50],
                                    },
                                    )
    response = await async_client.delete(f"/api/v1/organisation/organisation/{org.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Организация успешно удалена"
    mock_send_event.assert_called_once()


@pytest.mark.asyncio
@patch("org_app.api.send_organisation_delete_event", autospec=True)
async def test_delete_organisation_with_incorrect_id_type(mock_send_event: AsyncMock,
                                                          async_client: AsyncClient,
                                                          db_session: AsyncSession,
                                                          ) -> None:
    """
    Проверяем, что при указании неверного типа ID выведется ошибка
    :param mock_send_event: Мок-функция для отправки события об удалении всех организаций.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания организации в тестах.
    :return: None
    """

    response = await async_client.delete(f"/api/v1/organisation/organisation/FAKE_ID/")
    resp_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    missing_name_error = next(
        (
            error
            for error in resp_data["detail"]
            if error["type"] == "int_parsing" and "organisation_id" in error["loc"]
        ),
        None,
    )
    assert missing_name_error is not None
    assert missing_name_error["msg"] == "Input should be a valid integer, unable to parse string as an integer"
    mock_send_event.assert_not_called()
