from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import AsyncSessionLocal
from events import send_organisation_created_event, send_organisations_delete_event

router = APIRouter()


async def get_db() -> AsyncSession:
    """
    Получение сессии базы данных.

    :return: асинхронная сессия базы данных
    """

    async with AsyncSessionLocal() as session:
        yield session


@router.post("/organisations/", response_model=schemas.Organisation)
async def create_organisation(
    org: schemas.OrganisationCreate,
    db: AsyncSession = Depends(get_db)
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
async def get_organisations(db: AsyncSession = Depends(get_db)) -> list[schemas.Organisation]:
    """
    Получение списка всех организаций.

    :param db: сессия базы данных
    :return: список организаций
    """

    return await crud.get_all_organisations(db)


@router.delete("/organisations/", response_model=list[schemas.Organisation])
async def delete_all_organisations(db: AsyncSession = Depends(get_db)) -> list[schemas.Organisation]:
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
