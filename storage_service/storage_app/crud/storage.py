from typing import Sequence
from typing import Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from storage_app.models.storage import Storage
from storage_app.schemas.storage import StorageCreateSchema


async def create_storage(db: AsyncSession, storage: StorageCreateSchema) -> Storage:
    """
    :param db: Сессия базы данных
    :param storage: Данные для создания хранилища
    :return: Созданное хранилище

    Создает новое хранилище в базе данных и возвращает созданную запись.
    """

    # Проверяем, существует ли хранилище с таким именем
    existing_storage = await db.execute(select(Storage).where(Storage.name == storage.name))
    if existing_storage.scalars().first():
        raise HTTPException(
            status_code=400,
            detail=f"Хранилище с именем {storage.name} уже существует",
        )

    # Проверяем, чтобы количество отходов не превышало вместимость
    for waste_type, values in storage.capacity.items():
        if values[0] > values[1]:
            raise HTTPException(
                status_code=400,
                detail=f"Переполнение для отхода {waste_type}: {values[0]} превышает вместимость {values[1]}"
            )

    db_storage = Storage(name=storage.name, location=storage.location, capacity=storage.capacity)
    db.add(db_storage)
    await db.commit()
    await db.refresh(db_storage)

    return db_storage


async def get_all_storages(db: AsyncSession) -> Sequence[Storage]:
    """
    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает список всех хранилищ в базе данных.
    """

    result = await db.execute(select(Storage))

    return result.scalars().all()


async def delete_storage(db: AsyncSession, storage_id: int) -> Union[Storage, None]:
    """
    :param db: асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :return: объект удаленного хранилища
    """

    result = await db.execute(select(Storage).filter_by(id=storage_id))
    storage = result.scalars().first()

    if not storage:
        return None

    await db.delete(storage)
    await db.commit()

    return storage


async def update_storage_capacity(db: AsyncSession, storage_id: int, waste_data: dict) -> Union[Storage, None]:
    """
    :param db: Асинхронная сессия базы данных
    :param storage_id: Идентификатор хранилища
    :param waste_data: Словарь отходов, которые помещены в данное хранилище утилизировать - {"Пластик": 10, "Биоотходы": 50}
    :return: Обновленное хранилище
    """

    result = await db.execute(select(Storage).filter_by(id=storage_id))
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
