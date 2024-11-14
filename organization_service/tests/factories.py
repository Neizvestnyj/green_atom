from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from org_app.crud.organisation import create_organisation as crud_create_organisation
from org_app.models.organisation import Organisation
from org_app.models.storage import StorageCopy
from org_app.models.storage_distance import StorageDistanceCopy
from org_app.schemas.organisation import OrganisationCreateSchema


async def create_organisation(db_session: AsyncSession,
                              name: str,
                              capacity: Dict[str, list[int]],
                              ) -> Organisation:
    """
    Создание новой организации в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :param name: Имя создаваемой организации.
    :param capacity: Словарь, содержащий типы отходов и их ёмкости.
    :return: Созданная организация.
    """

    organisation_data = OrganisationCreateSchema(name=name, capacity=capacity)
    organisation = await crud_create_organisation(db=db_session, org=organisation_data)
    await db_session.commit()
    await db_session.refresh(organisation)

    return organisation


async def create_storage(db_session: AsyncSession, capacity: Dict[str, list[int]]) -> StorageCopy:
    """
    Создание нового хранилища для отходов в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :param capacity: Словарь, содержащий типы отходов и ёмкости для хранилища.
    :return: Созданное хранилище.
    """

    storage = StorageCopy(capacity=capacity)
    db_session.add(storage)
    await db_session.commit()
    await db_session.refresh(storage)

    return storage


async def create_distance(db_session: AsyncSession,
                          storage_id: int,
                          organisation_id: int,
                          distance: int,
                          ) -> StorageDistanceCopy:
    """
    Установка расстояния между организацией и хранилищем.

    :param db_session: Сессия базы данных для выполнения запросов.
    :param storage_id: Идентификатор хранилища.
    :param organisation_id: Идентификатор организации.
    :param distance: Расстояние от хранилища до организации.
    :return: Созданная запись о расстоянии между организацией и хранилищем.
    """

    storage_distance = StorageDistanceCopy(
        storage_id=storage_id,
        organisation_id=organisation_id,
        distance=distance
    )
    db_session.add(storage_distance)
    await db_session.commit()
    await db_session.refresh(storage_distance)

    return storage_distance
