from typing import Dict

from pydantic import BaseModel


class OrganisationBase(BaseModel):
    """
    Базовая модель для организации.

    :param name: Название организации
    :param capacity: Словарь, где ключ - это тип ресурса (например, стекло, пластик), а значение - список ёмкостей
    """

    name: str
    capacity: Dict[str, list]


class OrganisationCreate(OrganisationBase):
    """
    Модель для создания организации. Наследует от `OrganisationBase` и используется для создания новых записей.
    """

    pass


class Organisation(OrganisationBase):
    """
    Модель организации с ID. Используется для представления организации после её создания.

    :param id: Уникальный идентификатор организации
    :param name: Название организации
    :param capacity: Словарь типов ресурсов и их ёмкостей
    """

    id: int

    class Config:
        from_attributes = True  # Включает возможность создания модели из атрибутов объекта


class StorageCopyBase(BaseModel):
    """
    Базовая модель для хранения копии данных хранилища.

    :param capacity: Словарь, где ключ - это тип ресурса, а значение - список ёмкостей хранилища
    """

    capacity: Dict[str, list]


class StorageCopy(StorageCopyBase):
    """
    Модель копии хранилища с ID. Представляет копию данных хранилища в базе данных.

    :param id: Уникальный идентификатор копии хранилища
    :param capacity: Словарь типов ресурсов и их ёмкостей в хранилище
    """

    id: int

    class Config:
        from_attributes = True


class StorageDistanceCopyBase(BaseModel):
    """
    Базовая модель для хранения копии данных о расстоянии между хранилищем и организацией.

    :param storage_id: Идентификатор хранилища
    :param organisation_id: Идентификатор организации
    :param distance: Расстояние между хранилищем и организацией
    """

    storage_id: int
    organisation_id: int
    distance: float


class StorageDistanceCopy(StorageDistanceCopyBase):
    """
    Модель копии данных о расстоянии между хранилищем и организацией с ID.

    :param id: Уникальный идентификатор записи о расстоянии
    :param storage_id: Идентификатор хранилища
    :param organisation_id: Идентификатор организации
    :param distance: Расстояние между хранилищем и организацией
    """

    id: int

    class Config:
        from_attributes = True


class RecycleRequest(BaseModel):
    """
    Модель запроса на утилизацию отходов.

    :param organisation_id: Идентификатор организации, запрашивающей утилизацию
    """

    organisation_id: int


class RecycleResponse(BaseModel):
    """
    Модель ответа на запрос утилизации, содержащая план утилизации по хранилищам.

    :param storage_plan: Словарь, содержащий ID хранилища и объемы отходов, которые
                         можно туда передать.
                         Пример: {1: {"Стекло": 50, "Биоотходы": 100}, 2: {"Стекло": 50}}
    """

    storage_plan: Dict[int, Dict[str, int]]
