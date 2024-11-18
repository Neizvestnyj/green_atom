from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from org_app.models.storage import StorageCopy
from org_app.schemas.storage import StorageCopySchema


async def create_storage_copy(db: AsyncSession, storage: StorageCopySchema) -> StorageCopy:
    """
    Создание копии хранилища.

    :param db: асинхронная сессия базы данных
    :param storage: данные для создания хранилища
    :return: созданная копия хранилища
    """

    db_storage_copy = StorageCopy(id=storage.id, capacity=storage.capacity)
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


async def delete_storage(db: AsyncSession, storage_id: int) -> Union[StorageCopy, None]:
    """
    Удаление хранилища из БД.

    :param db: асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :return: список удаленных организаций
    """

    # Получаем все организации
    result = await db.execute(select(StorageCopy).filter_by(id=storage_id))
    storage = result.scalars().first()

    if not storage:
        return None

    await db.delete(storage)
    await db.commit()

    return storage


async def update_storage_copy_capacity(db: AsyncSession, storage_id: int, waste_data: dict) -> Union[StorageCopy, None]:
    """
    Обновляем информацию о хранилище

    :param db: Асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :param waste_data: Словарь отходов, которые помещены в данное хранилище утилизировать - {"Пластик": 10, "Биоотходы": 50}
    :return: Обновленное хранилище
    """

    # Используем асинхронный запрос для поиска организации по id
    result = await db.execute(select(StorageCopy).filter_by(id=storage_id))
    storage = result.scalars().first()

    if storage:
        # Обновляем capacity для каждого типа отходов
        for waste_type, amount in waste_data.items():
            # Обновляем текущий объем отходов
            storage.capacity[waste_type][0] += amount

        flag_modified(storage, 'capacity')
        db.add(storage)
        await db.commit()

        return storage
    else:
        return None
