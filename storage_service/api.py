from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import AsyncSessionLocal
from events import send_storage_created_event, send_storage_distance_created_event

router = APIRouter()


async def get_db() -> AsyncSession:
    """
    Функция для получения сессии базы данных.

    :return: AsyncSession

    Открывает сессию базы данных и предоставляет её для дальнейших операций.
    """

    async with AsyncSessionLocal() as session:
        yield session


@router.post("/storages/", response_model=schemas.Storage)
async def create_storage(
    storage: schemas.StorageCreate, db: AsyncSession = Depends(get_db)
) -> schemas.Storage:
    """
    Создание нового хранилища.

    :param storage: Данные для создания нового хранилища
    :param db: Сессия базы данных
    :return: Созданное хранилище

    Создает новое хранилище в базе данных, вызывает событие `send_storage_created_event` и возвращает созданное хранилище.
    """

    db_storage = await crud.create_storage(db, storage)
    send_storage_created_event(db_storage)

    return db_storage


@router.post("/storage_distances/", response_model=schemas.StorageDistance)
async def create_storage_distance(
    distance: schemas.StorageDistanceBase, db: AsyncSession = Depends(get_db)
) -> schemas.StorageDistance:
    """
    Создание записи о расстоянии между хранилищем и организацией.

    :param distance: Данные для создания записи о расстоянии
    :param db: Сессия базы данных
    :return: Созданная запись о расстоянии

    Создает новую запись о расстоянии, вызывает событие `send_storage_distance_created_event` и возвращает созданную запись.
    """

    db_distance = await crud.create_storage_distance(db, distance)
    send_storage_distance_created_event(db_distance)

    return db_distance


@router.get("/storages/", response_model=list[schemas.Storage])
async def get_storages(db: AsyncSession = Depends(get_db)) -> list[schemas.Storage]:
    """
    Получение списка всех хранилищ.

    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает все хранилища из базы данных.
    """

    return await crud.get_all_storages(db)


@router.get("/storage_distances/", response_model=list[schemas.StorageDistance])
async def get_storage_distances(
    db: AsyncSession = Depends(get_db)
) -> list[schemas.StorageDistance]:
    """
    Получение списка всех записей о расстояниях между хранилищами и организациями.

    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает все записи о расстояниях из базы данных.
    """

    return await crud.get_all_storage_distances(db)
