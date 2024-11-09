import os

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from storage_app.models import Base

# URL для подключения к базе данных SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///../storage_service.db")

# Создание асинхронного двигателя базы данных
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


# Включение поддержки внешних ключей для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """
    Включение поддержки внешних ключей в SQLite при подключении.

    :param dbapi_connection: Подключение к базе данных
    :param connection_record: Данные о подключении
    :return: None

    SQLite по умолчанию не поддерживает внешние ключи, эта настройка активирует их поддержку
    для текущего соединения.
    """

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
