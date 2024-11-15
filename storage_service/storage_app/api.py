from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.crud.storage import (create_storage as crud_create_storage,
                                      get_all_storages as crud_get_all_storages,
                                      )
from storage_app.crud.storage_distance import (get_all_storage_distances as crud_get_all_storage_distances,
                                               create_storage_distance as crud_create_storage_distance,
                                               )
from storage_app.events.producers.storage import send_storage_created_event
from storage_app.events.producers.storage_distance import send_storage_distance_created_event
from storage_app.models.storage import Storage
from storage_app.models.storage_distance import StorageDistance
from storage_app.schemas.storage import StorageSchema, StorageCreateSchema
from storage_app.schemas.storage_distance import StorageDistanceSchema, StorageDistanceBaseSchema
from .database import get_db

router = APIRouter()


@router.get("/health/")
async def health_check():
    return {"status": "OK"}


@router.post("/storages/", response_model=StorageSchema)
async def create_storage(
        storage: StorageCreateSchema,
        db: AsyncSession = Depends(get_db),
) -> Storage:
    """
    Создание нового хранилища.

    :param storage: Данные для создания нового хранилища
    :param db: Сессия базы данных
    :return: Созданное хранилище

    Создает новое хранилище в базе данных, вызывает событие `send_storage_created_event` и возвращает созданное хранилище.
    """

    db_storage = await crud_create_storage(db, storage)
    send_storage_created_event(db_storage)

    return db_storage


@router.post("/storage_distances/", response_model=StorageDistanceSchema)
async def create_storage_distance(
        distance: StorageDistanceBaseSchema,
        db: AsyncSession = Depends(get_db),
) -> StorageDistance:
    """
    Создание записи о расстоянии между хранилищем и организацией.

    :param distance: Данные для создания записи о расстоянии
    :param db: Сессия базы данных
    :return: Созданная запись о расстоянии

    Создает новую запись о расстоянии, вызывает событие `send_storage_distance_created_event` и возвращает созданную запись.
    """

    db_distance = await crud_create_storage_distance(db, distance)
    send_storage_distance_created_event(db_distance)

    return db_distance


@router.get("/storages/", response_model=list[StorageSchema])
async def get_storages(db: AsyncSession = Depends(get_db)) -> Sequence[Storage]:
    """
    Получение списка всех хранилищ.

    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает все хранилища из базы данных.
    """

    return await crud_get_all_storages(db)


@router.get("/storage_distances/", response_model=list[StorageDistanceSchema])
async def get_storage_distances(
        db: AsyncSession = Depends(get_db),
) -> Sequence[StorageDistance]:
    """
    Получение списка всех записей о расстояниях между хранилищами и организациями.

    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает все записи о расстояниях из базы данных.
    """

    return await crud_get_all_storage_distances(db)
