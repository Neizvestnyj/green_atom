import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_storage_distance(async_client: AsyncClient):
    """
    Проверяется, что сервис активен

    :param async_client: Асинхронный клиент для выполнения HTTP-запросов.
    :return: None
    """

    response = await async_client.get("/api/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "OK"
