from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation


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
            "Пластик": [0, 60],
            "Стекло": [0, 20],
            "Биоотходы": [0, 50]
        }
    }
    response = await async_client.post("/organisation/api/organisations/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert resp_data["name"] == data["name"]
    assert resp_data["capacity"] == data["capacity"]
    mock_send_event.assert_called_once()


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
                                  "Пластик": [0, 50],
                              },
                              )

    response = await async_client.get("/organisation/api/organisations/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_empty_organisations(async_client: AsyncClient) -> None:
    """
    Функция проверяет, что если нет организаций для удаления, возвращается ошибка с детализированным сообщением.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.delete("/organisation/api/organisations/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_json = response.json()
    assert response_json["detail"] == "Не найдено организаций для удаления"


@pytest.mark.asyncio
@patch("org_app.api.send_organisations_delete_event", autospec=True)
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

    await create_organisation(db_session,
                              name="New Test Organisation",
                              capacity={
                                  "Пластик": [0, 50],
                              },
                              )
    response = await async_client.delete("/organisation/api/organisations/")

    assert response.status_code == status.HTTP_200_OK
    mock_send_event.assert_called_once()
