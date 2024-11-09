from typing import Sequence

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import (create_organisation as crud_create_organisation,
                                       get_all_organisations as crud_get_all_organisations,
                                       delete_all_organisations as crud_delete_all_organisations,
                                       )
from org_app.events.send.organisation import send_organisation_created_event, \
    send_organisations_delete_event
from org_app.models.organisation import Organisation
from org_app.schemas.organisation import OrganisationSchema, OrganisationCreateSchema
from org_app.schemas.recycle import RecycleRequestSchema, RecycleResponseSchema
from org_app.services.waste_distribution import find_nearest_storage
from .database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "OK"}


@router.post("/organisations/", response_model=OrganisationSchema)
async def create_organisation(
        org: OrganisationCreateSchema,
        db: AsyncSession = Depends(get_db),
) -> Organisation:
    """
    Создание новой организации.

    :param org: данные для создания организации
    :param db: сессия базы данных
    :return: созданная организация
    """

    organisation = await crud_create_organisation(db, org)
    send_organisation_created_event(organisation)

    return organisation


@router.get("/organisations/", response_model=list[OrganisationSchema])
async def get_organisations(db: AsyncSession = Depends(get_db)) -> Sequence[Organisation]:
    """
    Получение списка всех организаций.

    :param db: сессия базы данных
    :return: список организаций
    """

    return await crud_get_all_organisations(db)


@router.delete("/organisations/", response_model=list[OrganisationSchema])
async def delete_all_organisations(db: AsyncSession = Depends(get_db)) -> Sequence[Organisation]:
    """
    Удаление всех организаций.

    :param db: сессия базы данных
    :return: список удаленных организаций
    :raises HTTPException: если организации для удаления не найдены
    """

    organisations = await crud_delete_all_organisations(db)
    if not organisations:
        raise HTTPException(status_code=404, detail="No organisations found to delete")

    send_organisations_delete_event(organisations)

    return organisations


@router.post("/recycle", response_model=RecycleResponseSchema)
async def recycle(
        recycle_request: RecycleRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Запрос на утилизацию отходов.

    :param recycle_request: запрос, содержащий ID организации и список типов отходов.
    :param db: асинхронная сессия базы данных.
    :return: словарь с хранилищами и количеством отходов для отправки.
    """

    # Находим ближайшие доступные хранилища и определяем, куда можно поместить отходы
    storage_plan = await find_nearest_storage(db, recycle_request.organisation_id)

    if not storage_plan:
        raise HTTPException(status_code=404, detail="Нет доступных хранилищ для утилизации отходов")

    return RecycleResponseSchema(storage_plan=storage_plan)
