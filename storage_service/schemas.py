from typing import Dict
from pydantic import BaseModel


class StorageBase(BaseModel):
    """
    Базовая модель для хранения информации о хранилище.

    :param name: Название хранилища.
    :param location: Местоположение хранилища.
    :param capacity: Вместимость хранилища, представляемая как словарь.
                      Ключами могут быть типы материалов (например, "стекло", "пластик"),
                      а значениями — списки с количеством или другим данными о материалах.
    """

    name: str
    location: str
    capacity: Dict[str, list]


class StorageCreate(StorageBase):
    """
    Модель для создания нового хранилища. Наследует от StorageBase.

    Используется при создании нового хранилища, например, через API.
    """

    pass


class Storage(StorageBase):
    """
    Модель для хранения информации о хранилище с его уникальным идентификатором.

    :param id: Уникальный идентификатор хранилища в базе данных.
    """

    id: int

    class Config:
        """
        Конфигурация модели Pydantic.

        :from_attributes: Указывает, что модель может быть автоматически
        создана из атрибутов SQLAlchemy модели, например, при запросе
        из базы данных.
        """

        from_attributes = True


class OrganisationCopy(BaseModel):
    """
    Модель для хранения информации о копии организации.

    :param id: Уникальный идентификатор копии организации.
    """

    id: int


class StorageDistanceBase(BaseModel):
    """
    Базовая модель для хранения информации о расстоянии между хранилищем и организацией.

    :param storage_id: Идентификатор хранилища.
    :param organisation_id: Идентификатор копии организации.
    :param distance: Расстояние между хранилищем и организацией (например, в километрах).
    """

    storage_id: int
    organisation_id: int
    distance: float


class StorageDistance(StorageDistanceBase):
    """
    Модель для хранения информации о расстоянии между хранилищем и организацией с уникальным идентификатором.

    :param id: Уникальный идентификатор записи о расстоянии.
    """

    id: int

    class Config:
        """
        Конфигурация модели Pydantic для StorageDistance.

        :from_attributes: Указывает, что модель может быть автоматически
        создана из атрибутов SQLAlchemy модели, например, при запросе
        из базы данных.
        """
        from_attributes = True
