from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.crud.storage import (create_storage as crud_create_storage,
                                      get_all_storages as crud_get_all_storages,
                                      delete_storage as crud_delete_storage,
                                      )
from storage_app.crud.storage_distance import (get_all_storage_distances as crud_get_all_storage_distances,
                                               create_storage_distance as crud_create_storage_distance,
                                               delete_distance as crud_delete_distance,
                                               )
from storage_app.events.producers.storage import send_storage_created_event, send_storage_deleted_event
from storage_app.events.producers.storage_distance import send_storage_distance_created_event, \
    send_distance_deleted_event
from storage_app.models.storage import Storage
from storage_app.models.storage_distance import StorageDistance
from storage_app.schemas.storage import StorageSchema, StorageCreateSchema
from storage_app.schemas.storage_distance import StorageDistanceSchema, StorageDistanceBaseSchema
from .database import get_db

router = APIRouter()


@router.get("/health/")
async def health_check():
    return {"status": "OK"}


@router.post("/storage/", response_model=StorageSchema)
async def create_storage(
        storage: StorageCreateSchema,
        db: AsyncSession = Depends(get_db),
) -> Storage:
    """
    :param storage: Данные для создания нового хранилища
    :param db: Сессия базы данных
    :return: Созданное хранилище

    Создает новое хранилище в базе данных, вызывает событие `send_storage_created_event` и возвращает созданное хранилище.
    """

    db_storage = await crud_create_storage(db, storage)
    send_storage_created_event(db_storage)

    return db_storage


@router.post("/distance/", response_model=StorageDistanceSchema)
async def create_storage_distance(
        distance: StorageDistanceBaseSchema,
        db: AsyncSession = Depends(get_db),
) -> StorageDistance:
    """
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
    :param db: Сессия базы данных
    :return: Список хранилищ

    Возвращает все хранилища из базы данных.
    """

    return await crud_get_all_storages(db)


@router.get("/distances/", response_model=list[StorageDistanceSchema])
async def get_storage_distances(
        db: AsyncSession = Depends(get_db),
) -> Sequence[StorageDistance]:
    """
    :param db: Сессия базы данных
    :return: Список записей о расстояниях

    Возвращает все записи о расстояниях из базы данных.
    """

    return await crud_get_all_storage_distances(db)


@router.delete("/storage/{storage_id}/")
async def delete_storage(storage_id: int, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    :param storage_id: ID хранилища
    :param db: сессия базы данных
    :return: сообщение о том, что хранилище удалено
    :raises HTTPException: если организация для удаления не найдены
    """

    storage = await crud_delete_storage(db, storage_id)
    if not storage:
        raise HTTPException(status_code=404, detail="Не найдено хранилища для удаления")

    send_storage_deleted_event(storage)

    return JSONResponse(content={"message": "Хранилище успешно удалено"}, status_code=200)


@router.delete("/distance/{distance_id}/")
async def delete_storage_distance(distance_id: int, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    :param distance_id: ID расстояния
    :param db: сессия базы данных
    :return: сообщение о том, что расстояние удалено
    :raises HTTPException: если расстояние для удаления не найдены
    """

    distance = await crud_delete_distance(db, distance_id)
    if not distance:
        raise HTTPException(status_code=404, detail="Не найдено расстояние между МНО и ОО для удаления")

    send_distance_deleted_event(distance)

    return JSONResponse(content={"message": "Расстояние между ОО и МНО успешно удалено"}, status_code=200)
