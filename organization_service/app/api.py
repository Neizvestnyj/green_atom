from typing import Sequence

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
import schemas
from database import get_db
from events import send_organisation_created_event, send_organisations_delete_event

router = APIRouter()


@router.post("/organisations/", response_model=schemas.Organisation)
async def create_organisation(
        org: schemas.OrganisationCreate,
        db: AsyncSession = Depends(get_db),
) -> schemas.Organisation:
    """
    Создание новой организации.

    :param org: данные для создания организации
    :param db: сессия базы данных
    :return: созданная организация
    """

    organisation = await crud.create_organisation(db, org)
    send_organisation_created_event(organisation)

    return organisation


@router.get("/organisations/", response_model=list[schemas.Organisation])
async def get_organisations(db: AsyncSession = Depends(get_db)) -> Sequence[models.Organisation]:
    """
    Получение списка всех организаций.

    :param db: сессия базы данных
    :return: список организаций
    """

    return await crud.get_all_organisations(db)


@router.delete("/organisations/", response_model=list[schemas.Organisation])
async def delete_all_organisations(db: AsyncSession = Depends(get_db)) -> Sequence[models.Organisation]:
    """
    Удаление всех организаций.

    :param db: сессия базы данных
    :return: список удаленных организаций
    :raises HTTPException: если организации для удаления не найдены
    """

    organisations = await crud.delete_all_organisations(db)
    if not organisations:
        raise HTTPException(status_code=404, detail="No organisations found to delete")

    send_organisations_delete_event(organisations)

    return organisations


@router.post("/recycle", response_model=schemas.RecycleResponse)
async def recycle(
        recycle_request: schemas.RecycleRequest,
        db: AsyncSession = Depends(get_db),
):
    """
    Запрос на утилизацию отходов.

    :param recycle_request: запрос, содержащий ID организации и список типов отходов.
    :param db: асинхронная сессия базы данных.
    :return: словарь с хранилищами и количеством отходов для отправки.
    """

    # Находим ближайшие доступные хранилища и определяем, куда можно поместить отходы
    storage_plan = await crud.find_nearest_storage(db, recycle_request.organisation_id)

    if not storage_plan:
        raise HTTPException(status_code=404, detail="Нет доступных хранилищ для утилизации отходов")

    return schemas.RecycleResponse(storage_plan=storage_plan)
