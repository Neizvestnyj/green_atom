import os

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from org_app.models import Base

# URL подключения к базе данных
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///../organisation_service.db")

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Создание асинхронной сессии
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """
    Инициализация базы данных: создание всех таблиц, если их еще нет.

    :return: None

    Функция выполняет создание таблиц в базе данных, если они еще не существуют.
    """

    async with engine.begin() as conn:
        # Выполняем синхронно создание таблиц в базе данных
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """
    Получение сессии базы данных.

    :return: асинхронная сессия базы данных
    """

    async with AsyncSessionLocal() as session:
        yield session


# Включение поддержки внешних ключей для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """
    Устанавливает флаг для поддержки внешних ключей в SQLite.

    :param dbapi_connection: подключение к базе данных
    :param connection_record: запись подключения
    :return: None

    Включает поддержку внешних ключей в базе данных SQLite, что важно для
    соблюдения ограничений целостности данных.
    """

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()