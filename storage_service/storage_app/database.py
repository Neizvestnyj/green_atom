import os

from sqlalchemy import event
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.base import _ConnectionRecord

from storage_app.models import Base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL",
                                    "sqlite+aiosqlite:///../storage_service.db"
                                    )

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Сессия для работы с базой данных
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """
    Инициализация базы данных: создание всех таблиц, если они ещё не существуют.

    :return: None

    Используется для создания всех таблиц, определённых в модели базы данных, при старте приложения.
    """

    async with engine.begin() as conn:
        # Создание всех таблиц в базе данных
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """
    Функция для получения сессии базы данных.

    :return: AsyncSession

    Открывает сессию базы данных и предоставляет её для дальнейших операций.
    """

    async with AsyncSessionLocal() as session:
        yield session


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: AsyncAdapt_aiosqlite_connection, connection_record: _ConnectionRecord) -> None:
    """
    :param dbapi_connection: подключение к базе данных
    :param connection_record: запись подключения
    :return: None

    Включает поддержку внешних ключей в базе данных SQLite, что важно для
    соблюдения ограничений целостности данных.
    """

    if isinstance(dbapi_connection, AsyncAdapt_aiosqlite_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
