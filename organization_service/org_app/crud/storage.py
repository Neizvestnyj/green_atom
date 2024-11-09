from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.models.storage import StorageCopy


async def create_storage_copy(db: AsyncSession, storage_id: int, capacity: dict) -> StorageCopy:
    """
    Создание копии хранилища.

    :param db: асинхронная сессия базы данных
    :param storage_id: идентификатор хранилища
    :param capacity: вместимость хранилища
    :return: созданная копия хранилища
    """

    db_storage_copy = StorageCopy(id=storage_id, capacity=capacity)
    db.add(db_storage_copy)
    await db.commit()
    await db.refresh(db_storage_copy)

    return db_storage_copy


async def get_storage_copy(db: AsyncSession, storage_id: int) -> StorageCopy:
    """
    Возвращает копию хранилища по ID.

    :param db: Асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :return: Копия хранилища или None, если копия не найдена
    """
    result = await db.execute(select(StorageCopy).where(StorageCopy.id == storage_id))

    return result.scalars().first()
