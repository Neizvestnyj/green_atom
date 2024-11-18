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
    Проверяем, что пытаемся переработать отходы несуществующей организации

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation_id = 100
    data = {"organisation_id": organisation_id}

    response = await async_client.post("/api/v1/organisation/recycle/", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Организация с идентификатором {organisation_id} не найдена"


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_all_waste(mock_update_storage: AsyncMock,
                                 async_client: AsyncClient,
                                 db_session: AsyncSession) -> None:
    """
    Проверка полного и корректного распределения отходов

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={"Пластик": [50, 50],
                  "Стекло": [40, 40],
                  "Биоотходы": [20, 20],
                  }
    )

    storage1 = await create_storage(db_session, {"Пластик": [0, 30], "Биоотходы": [0, 20]})
    storage2 = await create_storage(db_session, {"Стекло": [0, 50], "Пластик": [0, 20]})

    await create_distance(db_session, storage1.id, organisation.id, distance=10)
    await create_distance(db_session, storage2.id, organisation.id, distance=20)

    data = {"organisation_id": organisation.id}

    response = await async_client.post("/api/v1/organisation/recycle/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['waste_distribution'] == {'1': {'Пластик': 30, 'Биоотходы': 20},
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
    Проверяем, что не получится отправить на переработки отходы, если они уже отправлены

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [50, 50],
        }
    )
    storage1 = await create_storage(db_session, {"Пластик": [0, 60], "Биоотходы": [0, 20]})
    await create_distance(db_session, storage1.id, organisation.id, distance=10)

    data = {"organisation_id": organisation.id}

    await async_client.post("/api/v1/organisation/recycle/", json=data)
    assert mock_update_storage.call_count == 1
    response = await async_client.post("/api/v1/organisation/recycle/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Все отходы уже были успешно переработаны"


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_no_storage_available(mock_update_storage: AsyncMock,
                                            async_client: AsyncClient,
                                            db_session: AsyncSession) -> None:
    """
    Проверяем, что не можем распределить отходы по хранилищам, так как они заполнены

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [50, 50],
        }
    )
    storage1 = await create_storage(db_session, {"Пластик": [30, 30], "Биоотходы": [20, 20]})
    await create_distance(db_session, storage1.id, organisation.id, distance=10)

    data = {"organisation_id": organisation.id}
    response = await async_client.post("/api/v1/organisation/recycle/", json=data)

    mock_update_storage.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Нет доступных хранилищ для утилизации отходов"


@pytest.mark.asyncio
@patch("org_app.api.send_update_capacity_event")
async def test_recycle_partial_delivery(mock_update_storage: AsyncMock,
                                        async_client: AsyncClient,
                                        db_session: AsyncSession) -> None:
    """
    Проверяем, что часть отходов может быть доставлена в хранилище, а часть — нет.

    :param mock_update_storage: Мок-функция для отправки события об обновлении ёмкости хранилища.
    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [50, 50],
            "Биоотходы": [50, 50],
        }
    )
    storage1 = await create_storage(db_session, {"Пластик": [10, 30], "Биоотходы": [10, 20]})
    await create_distance(db_session, storage1.id, organisation.id, distance=100)

    data = {"organisation_id": organisation.id}
    response = await async_client.post("/api/v1/organisation/recycle/", json=data)
    resp_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert resp_data[
               "message"] == "Отходы частично распределены. Не удалось отправить: {'Пластик': 30, 'Биоотходы': 40} из-за ограничений"
    assert mock_update_storage.call_count == 1


@pytest.mark.asyncio
async def test_no_storage_connection_for_organisation(async_client: AsyncClient,
                                                      db_session: AsyncSession,
                                                      ) -> None:
    """
    Проверяем, что при попытке распределить отходы организации, у которой нет связи с хранилищами получим ошибку

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :param db_session: Сессия базы данных для создания данных в тестах.
    :return: None
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [50, 50],
        }
    )
    data = {"organisation_id": organisation.id}

    response = await async_client.post("/api/v1/organisation/recycle/", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"У организации нет связи с каким либо хранилищем"
