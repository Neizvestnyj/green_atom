from typing import Sequence

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import (create_organisation as crud_create_organisation,
                                       get_all_organisations as crud_get_all_organisations,
                                       delete_organisation as crud_delete_organisation,
                                       update_organisation_capacity as crud_update_organisation_capacity,
                                       )
from org_app.crud.storage import update_storage_copy_capacity as crud_update_storage_copy_capacity
from org_app.events.producers.organisation import (send_organisation_created_event,
                                                   send_organisation_delete_event,
                                                   )
from org_app.events.producers.storage import send_update_capacity_event
from org_app.models.organisation import Organisation
from org_app.schemas.organisation import OrganisationSchema, OrganisationCreateSchema
from org_app.schemas.recycle import RecycleRequestSchema, RecycleResponseSchema
from org_app.services.waste_distribution import find_nearest_storage
from .database import get_db

router = APIRouter()


@router.get("/health/")
async def health_check():
    return {"status": "OK"}


@router.post("/organisation/", response_model=OrganisationSchema)
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


@router.delete("/organisation/{organisation_id}/")
async def delete_organisation(organisation_id: int, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    Удаление организации.

    :param organisation_id: ID организации
    :param db: сессия базы данных
    :return: список удаленных организаций
    :raises HTTPException: если организации для удаления не найдены
    """

    organisation = await crud_delete_organisation(db, organisation_id)
    if not organisation:
        raise HTTPException(status_code=404, detail="Не найдено организации для удаления")

    send_organisation_delete_event(organisation)

    return JSONResponse(content={"message": "Организация успешно удалена"}, status_code=200)


@router.post("/recycle/", response_model=RecycleResponseSchema)
async def recycle(
        recycle_request: RecycleRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Запрос на утилизацию отходов.

    :param recycle_request: запрос, содержащий ID организации и список типов отходов.
    :param db: асинхронная сессия базы данных.
    :return: словарь с хранилищами и количеством отходов для отправки, а также сообщение
    """

    org_id = recycle_request.organisation_id
    organisation = await db.get(Organisation, org_id)

    if not organisation:
        raise HTTPException(status_code=404, detail=f"Организация с идентификатором {org_id} не найдена")

    if organisation.is_all_waste_processed():
        return RecycleResponseSchema(waste_distribution={}, message="Все отходы уже были успешно переработаны")

    # Находим ближайшие доступные хранилища и определяем, куда можно поместить отходы
    storage_plan, total_sent_waste, remaining_waste = await find_nearest_storage(db, org_id)

    if not storage_plan:
        raise HTTPException(status_code=404, detail="Нет доступных хранилищ для утилизации отходов")

    await crud_update_organisation_capacity(db, recycle_request.organisation_id, total_sent_waste)

    for storage_id in storage_plan:
        updated_capacity = storage_plan[storage_id]
        await crud_update_storage_copy_capacity(db, storage_id, updated_capacity)
        send_update_capacity_event(storage_id, updated_capacity)

    if remaining_waste:
        return RecycleResponseSchema(
            waste_distribution=storage_plan,
            message=f"Отходы частично распределены. Не удалось отправить: {remaining_waste} из-за ограничений"
        )
    else:
        return RecycleResponseSchema(waste_distribution=storage_plan,
                                     message="Отходы были распределены по хранилищам"
                                     )
