from typing import Dict

from pydantic import BaseModel, ConfigDict


class StorageSchemaBaseSchema(BaseModel):
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


class StorageSchemaCreateSchema(StorageSchemaBaseSchema):
    """
    Модель для создания нового хранилища. Наследует от StorageSchemaBaseSchema.

    Используется при создании нового хранилища, например, через API.
    """

    pass


class StorageSchema(StorageSchemaBaseSchema):
    """
    Модель для хранения информации о хранилище с его уникальным идентификатором.

    :param id: Уникальный идентификатор хранилища в базе данных.
    :param model_config: Конфигурация модели для автоматического извлечения значений атрибутов из ORM-модели.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
