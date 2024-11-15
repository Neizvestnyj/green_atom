from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from org_app.database import get_db, init_db, Base
from org_app.main import app

# URL тестовой базы данных
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создание асинхронного движка и фабрики сессий для тестирования
test_engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Переопределение зависимости для получения сессии базы данных.

    :return: Сессия базы данных для тестирования.
    """

    async with TestSessionLocal() as session:
        yield session


async def override_init_db() -> None:
    """
    Создание всех таблиц для тестов, если они ещё не существуют.

    :return: None
    """

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database() -> None:
    """
    Создает и настраивает тестовую базу данных, а также переопределяет зависимости FastAPI.
    После выполнения тестов очищает базу данных.

    :return: None
    """

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[init_db] = override_init_db

    await override_init_db()
    print('Database initialized and dependencies overridden')

    yield  # выполнение тестов

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print('Database cleaned up')


@pytest_asyncio.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Предоставляет клиент для взаимодействия с FastAPI, который используется для выполнения HTTP-запросов в тестах.

    :return: Экземпляр клиента для выполнения тестовых запросов.
    """

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает и возвращает сессию базы данных для работы с данными в тестах.

    :return: Сессия базы данных для выполнения запросов.
    """

    async with TestSessionLocal() as session:
        yield session
