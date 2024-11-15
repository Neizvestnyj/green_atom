from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation, create_storage, create_distance


@pytest.mark.asyncio
async def test_recycle_empty_organisation(async_client: AsyncClient,
                                          db_session: AsyncSession,
                                          ) -> None:
    """
    Функция создает организацию и два хранилища, затем проверяет перераспределение отходов по хранилищам с учётом расстояний.

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation_id = 100
    data = {"organisation_id": organisation_id}

    response = await async_client.post("/organisation/api/recycle/", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Организация с идентификатором {organisation_id} не найдена"


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_all_waste(mock_update_storage: AsyncMock,
                                 async_client: AsyncClient,
                                 db_session: AsyncSession) -> None:
    """
    Функция создает организацию и два хранилища, затем проверяет перераспределение отходов по хранилищам с учётом расстояний.

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={"Пластик": [0, 50],
                  "Стекло": [0, 40],
                  "Биоотходы": [0, 20],
                  }
    )

    storage1 = await create_storage(db_session, {"Пластик": [0, 30], "Биоотходы": [0, 20]})
    storage2 = await create_storage(db_session, {"Стекло": [0, 50], "Пластик": [0, 20]})

    await create_distance(db_session, storage1.id, organisation.id, distance=10)
    await create_distance(db_session, storage2.id, organisation.id, distance=20)

    data = {"organisation_id": organisation.id}

    response = await async_client.post("/organisation/api/recycle/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['storage_plan'] == {'1': {'Пластик': 30, 'Биоотходы': 20},
                                               '2': {'Пластик': 20, 'Стекло': 40},
                                               }
    assert response.json()["message"] == "Отходы были распределены по хранилищам"
    assert mock_update_storage.call_count == 2


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_all_waste_already_processed(mock_update_storage: AsyncMock,
                                                   async_client: AsyncClient,
                                                   db_session: AsyncSession) -> None:
    """
    Функция создает организацию и одно хранилище, а затем дважды вызывает перераспределение отходов.

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [0, 50],
        }
    )
    storage1 = await create_storage(db_session, {"Пластик": [0, 60], "Биоотходы": [0, 20]})
    await create_distance(db_session, storage1.id, organisation.id, distance=10)

    data = {"organisation_id": organisation.id}

    await async_client.post("/organisation/api/recycle/", json=data)
    assert mock_update_storage.call_count == 1
    response = await async_client.post("/organisation/api/recycle/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Все отходы уже были успешно переработаны"


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_no_storage_available(mock_update_storage: AsyncMock,
                                            async_client: AsyncClient,
                                            db_session: AsyncSession) -> None:
    """
    Функция создает организацию и одно хранилище, но оно полностью заполнено.

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [0, 50],
        }
    )
    storage1 = await create_storage(db_session, {"Пластик": [30, 30], "Биоотходы": [20, 20]})
    await create_distance(db_session, storage1.id, organisation.id, distance=10)

    data = {"organisation_id": organisation.id}
    response = await async_client.post("/organisation/api/recycle/", json=data)

    mock_update_storage.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Нет доступных хранилищ для утилизации отходов"
