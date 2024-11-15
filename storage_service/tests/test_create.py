import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.crud.organisation import create_organisation_copy as crud_create_organisation_copy
from storage_app.crud.storage import create_storage as crud_create_storage
from storage_app.crud.storage_distance import create_storage_distance as crud_create_storage_distance
from storage_app.models.organisation import OrganisationCopy
from storage_app.models.storage import Storage
from storage_app.models.storage_distance import StorageDistance
from storage_app.schemas.organisation import OrganisationCopySchema
from storage_app.schemas.storage import StorageSchemaCreateSchema
from storage_app.schemas.storage_distance import StorageDistanceBaseSchema
from .factories import create_organisation, create_storage


@pytest.mark.asyncio
async def test_create_organisation(db_session: AsyncSession) -> None:
    """
    Создание новой организации в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    org_id = 1

    organisation_data = OrganisationCopySchema(id=org_id)
    organisation = await crud_create_organisation_copy(db=db_session, organisation=organisation_data)

    # Проверяем, что копия была успешно создана
    assert organisation.id == org_id

    # Проверяем, что копия присутствует в базе данных
    retrieved_org = await db_session.get(OrganisationCopy, organisation.id)
    assert retrieved_org is not None


@pytest.mark.asyncio
async def test_create_storage(db_session: AsyncSession) -> None:
    """
    Создание новой копии хранилища в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    name = 'МНО1'
    location = 'Москва'
    capacity = {"Пластик": [0, 60]}

    storage_data = StorageSchemaCreateSchema(name=name, location=location, capacity=capacity)
    storage = await crud_create_storage(db=db_session, storage=storage_data)

    # Проверяем, что хранилище было успешно создано
    assert storage.name == name
    assert storage.location == location
    assert storage.capacity == capacity

    # Проверяем, что хранилище присутствует в базе данных
    retrieved_storage = await db_session.get(Storage, storage.id)
    assert retrieved_storage is not None
    assert retrieved_storage.name == name
    assert retrieved_storage.capacity == capacity


@pytest.mark.asyncio
async def test_create_storage_distance_copy(db_session: AsyncSession) -> None:
    """
    Создание новой копии записи о расстоянии между хранилищем и организацией в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    organisation = await create_organisation(db_session)

    name = 'МНО1'
    location = 'Москва'
    capacity = {"Пластик": [0, 60]}
    storage = await create_storage(db_session, name, location, capacity)

    distance = 100
    storage_distance_data = StorageDistanceBaseSchema(storage_id=storage.id, organisation_id=organisation.id,
                                                      distance=distance)
    storage_distance = await crud_create_storage_distance(
        db=db_session,
        distance=storage_distance_data,
    )

    assert storage_distance.storage_id == storage.id
    assert storage_distance.organisation_id == organisation.id
    assert storage_distance.distance == distance

    retrieved_distance = await db_session.get(StorageDistance, storage_distance.id)
    assert retrieved_distance is not None
    assert retrieved_distance.storage_id == storage.id
    assert retrieved_distance.organisation_id == organisation.id
    assert retrieved_distance.distance == distance
