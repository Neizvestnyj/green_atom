from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from storage_app.models.organisation import OrganisationCopy
from storage_app.schemas.organisation import OrganisationCopySchema


async def create_organisation_copy(db: AsyncSession, organisation: OrganisationCopySchema) -> OrganisationCopy:
    """
    Создание копии записи об организации.

    :param db: Сессия базы данных
    :param organisation: данные для создания организации
    :return: `OrganisationCopy`
    """

    db_org_copy = OrganisationCopy(id=organisation.id)
    db.add(db_org_copy)
    await db.commit()

    return db_org_copy


async def delete_organisation_by_id(db: AsyncSession, organisation_id: int) -> None:
    """
    Удаление организации по ID.

    :param db: Сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: None
    """

    result = await db.execute(select(OrganisationCopy).filter(OrganisationCopy.id == organisation_id))
    organisation = result.scalars().first()

    if organisation:
        await db.delete(organisation)
        await db.commit()
