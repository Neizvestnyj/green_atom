import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import create_organisation, create_storage
from org_app.crud.organisation import create_organisation as crud_create_organisation
from org_app.crud.storage import create_storage_copy as crud_create_storage
from org_app.crud.storage_distance import create_storage_distance_copy as crud_create_storage_distance
from org_app.models.organisation import Organisation
from org_app.models.storage import StorageCopy
from org_app.models.storage_distance import StorageDistanceCopy
from org_app.schemas.organisation import OrganisationCreateSchema
from org_app.schemas.storage import StorageCopySchema
from org_app.schemas.storage_distance import StorageDistanceCopySchema


@pytest.mark.asyncio
async def test_create_organisation(db_session: AsyncSession) -> None:
    """
    Создание новой организации в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    name = 'ОО1'
    capacity = {"Пластик": [0, 60]}

    organisation_data = OrganisationCreateSchema(name=name, capacity=capacity)
    organisation = await crud_create_organisation(db=db_session, org=organisation_data)

    # Проверяем, что копия была успешно создана
    assert organisation.name == name
    assert organisation.capacity == capacity

    # Проверяем, что копия присутствует в базе данных
    retrieved_org = await db_session.get(Organisation, organisation.id)
    assert retrieved_org is not None
    assert retrieved_org.name == name
    assert retrieved_org.capacity == capacity


@pytest.mark.asyncio
async def test_create_storage_copy(db_session: AsyncSession) -> None:
    """
    Создание новой копии хранилища в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    storage_id = 1
    capacity = {"Пластик": [0, 60]}

    storage_data = StorageCopySchema(id=storage_id, capacity=capacity)
    storage_copy = await crud_create_storage(db=db_session, storage=storage_data)

    # Проверяем, что копия была успешно создана
    assert storage_copy.id == storage_id
    assert storage_copy.capacity == capacity

    # Проверяем, что копия присутствует в базе данных
    retrieved_storage_copy = await db_session.get(StorageCopy, storage_id)
    assert retrieved_storage_copy is not None
    assert retrieved_storage_copy.capacity == capacity


@pytest.mark.asyncio
async def test_create_storage_distance_copy(db_session: AsyncSession) -> None:
    """
    Создание новой копии записи о расстоянии между хранилищем и организацией в тестовой базе данных.

    :param db_session: Сессия базы данных для выполнения запросов.
    :return: `None`
    """

    organisation = await create_organisation(
        db_session,
        name="Test Organisation",
        capacity={
            "Пластик": [0, 50],
        }
    )
    storage = await create_storage(db_session, {"Пластик": [0, 30], "Биоотходы": [0, 20]})

    storage_distance_id = 1
    storage_id = storage.id
    organisation_id = organisation.id
    distance = 100

    storage_distance_data = StorageDistanceCopySchema(id=storage_distance_id,
                                                      storage_id=storage_id,
                                                      organisation_id=organisation_id,
                                                      distance=distance,
                                                      )
    storage_distance_copy = await crud_create_storage_distance(
        db=db_session,
        storage_distance=storage_distance_data,
    )

    # Проверяем, что копия была успешно создана
    assert storage_distance_copy.id == storage_distance_id
    assert storage_distance_copy.storage_id == storage_id
    assert storage_distance_copy.organisation_id == organisation_id
    assert storage_distance_copy.distance == distance

    # Проверяем, что копия присутствует в базе данных
    retrieved_distance_copy = await db_session.get(StorageDistanceCopy, storage_distance_id)
    assert retrieved_distance_copy is not None
    assert retrieved_distance_copy.storage_id == storage_id
    assert retrieved_distance_copy.organisation_id == organisation_id
    assert retrieved_distance_copy.distance == distance
