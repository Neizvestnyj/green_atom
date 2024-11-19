from typing import Sequence, Union

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from org_app.models.organisation import Organisation
from org_app.schemas.organisation import OrganisationCreateSchema


async def create_organisation(db: AsyncSession, org: OrganisationCreateSchema) -> Organisation:
    """
    Создание новой организации в базе данных.

    :param db: асинхронная сессия базы данных
    :param org: данные для создания организации
    :return: созданная организация
    """

    # Проверяем, существует ли организация с таким именем
    existing_org = await db.execute(select(Organisation).where(Organisation.name == org.name))
    if existing_org.scalars().first():
        raise HTTPException(
            status_code=400,
            detail=f"Организация с именем {org.name} уже существует",
        )

    # Проверяем, чтобы количество отходов не превышало вместимость
    for waste_type, values in org.capacity.items():
        if values[0] > values[1]:
            raise HTTPException(
                status_code=400,
                detail=f"Переполнение для отхода {waste_type}: {values[0]} превышает вместимость {values[1]}"
            )

    db_org = Organisation(name=org.name, capacity=org.capacity)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)

    return db_org


async def get_all_organisations(db: AsyncSession) -> Sequence[Organisation]:
    """
    Получение всех организаций из базы данных.

    :param db: асинхронная сессия базы данных
    :return: список организаций
    """

    result = await db.execute(select(Organisation))

    return result.scalars().all()


async def get_organisation(db: AsyncSession, organisation_id: int) -> Organisation:
    """
    Возвращает организацию по её ID.

    :param db: Асинхронная сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: Организация или None, если организация не найдена
    """

    result = await db.execute(select(Organisation).where(Organisation.id == organisation_id))

    return result.scalar_one_or_none()


async def update_organisation_capacity(db: AsyncSession,
                                       organisation_id: int,
                                       waste_data: dict,
                                       ) -> Union[Organisation, None]:
    """
    Обновляем информацию об организации

    :param db: Асинхронная сессия базы данных
    :param organisation_id: Идентификатор организации
    :param waste_data: Словарь отходов, которые удалось утилизировать - {"Пластик": 10, "Биоотходы": 50}
    :return: Обновленную организацию
    """

    result = await db.execute(select(Organisation).filter_by(id=organisation_id))
    organisation = result.scalars().first()

    if organisation:
        # Обновляем capacity в организации для каждого типа отходов
        for waste_type, amount in waste_data.items():
            # Обновляем текущий объем отходов
            organisation.capacity[waste_type][0] -= amount

        flag_modified(organisation, 'capacity')
        db.add(organisation)
        await db.commit()

        return organisation
    else:
        return None


async def delete_organisation(db: AsyncSession, organisation_id: int) -> Union[Organisation, None]:
    """
    Удаление организации из базы данных по ID.

    :param db: асинхронная сессия базы данных
    :param organisation_id: Идентификатор организации
    :return: удаленная организация
    """

    # Получаем все организации
    result = await db.execute(select(Organisation).filter_by(id=organisation_id))
    organisation = result.scalars().first()

    if not organisation:
        return None

    await db.delete(organisation)
    await db.commit()

    return organisation
