from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from storage_app.models.storage import Storage
from storage_app.schemas.storage import StorageSchemaCreateSchema


async def create_storage(db: AsyncSession, storage: StorageSchemaCreateSchema) -> Storage:
    """
    Создание нового хранилища.

    :param db: Сессия базы данных
    :param storage: Данные для создания хранилища
    :return: Созданное хранилище

    Создает новое хранилище в базе данных и возвращает созданную запись.
    """

    db_storage = Storage(name=storage.name, location=storage.location, capacity=storage.capacity)
    db.add(db_storage)
    await db.commit()
    await db.refresh(db_storage)

    return db_storage


async def get_all_storages(db: AsyncSession) -> Sequence[Storage]:
    """
    Получение всех хранилищ.

    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает список всех хранилищ в базе данных.
    """

    result = await db.execute(select(Storage))

    return result.scalars().all()
