from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from storage_service.app.models.organisation import OrganisationCopy


async def create_organisation_copy(db: AsyncSession, organisation_id: int) -> None:
    """
    Создание копии записи об организации.

    :param db: Сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: None

    Создает копию организации в базе данных.
    """

    db_org_copy = OrganisationCopy(id=organisation_id)
    db.add(db_org_copy)
    await db.commit()


async def delete_organisation_by_id(db: AsyncSession, organisation_id: int) -> None:
    """
    Удаление организации по ID.

    :param db: Сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: None

    Удаляет организацию и её связанные записи с помощью каскадного удаления.
    """

    result = await db.execute(select(OrganisationCopy).filter(OrganisationCopy.id == organisation_id))
    organisation = result.scalars().first()

    if organisation:
        await db.delete(organisation)
        await db.commit()
