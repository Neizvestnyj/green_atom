from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.models.organisation import OrganisationCopy
from storage_app.models.storage import Storage
from storage_app.models.storage_distance import StorageDistance


async def create_organisation(db_session: AsyncSession) -> OrganisationCopy:
    """
    Создание новой организации в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: Созданная организация.
    """

    organisation = OrganisationCopy()
    db_session.add(organisation)
    await db_session.commit()
    await db_session.refresh(organisation)

    return organisation


async def create_storage(db_session: AsyncSession,
                         name: str,
                         location: str,
                         capacity: Dict[str, list[int]],
                         ) -> Storage:
    """
    Функция создает хранилище с указанной ёмкостью для хранения отходов.

    :param db_session: Сессия базы данных для выполнения запросов.
    :param name: Имя создаваемого хранилища.
    :param location: Расположение создаваемого хранилища.
    :param capacity: Словарь, содержащий типы отходов и ёмкости для хранилища.
    :return: Созданное хранилище.
    """

    storage = Storage(name=name, location=location, capacity=capacity)
    db_session.add(storage)
    await db_session.commit()
    await db_session.refresh(storage)

    return storage


async def create_distance(db_session: AsyncSession,
                          storage_id: int,
                          organisation_id: int,
                          distance: int,
                          ) -> StorageDistance:
    """
    Функция создает запись о расстоянии между организацией и хранилищем.

    :param db_session: Сессия базы данных для выполнения запросов.
    :param storage_id: Идентификатор хранилища.
    :param organisation_id: Идентификатор организации.
    :param distance: Расстояние от хранилища до организации.
    :return: Созданная запись о расстоянии между организацией и хранилищем.
    """

    storage_distance = StorageDistance(
        storage_id=storage_id,
        organisation_id=organisation_id,
        distance=distance
    )
    db_session.add(storage_distance)
    await db_session.commit()
    await db_session.refresh(storage_distance)

    return storage_distance
