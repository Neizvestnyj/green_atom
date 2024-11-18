from typing import Dict

from pydantic import BaseModel, ConfigDict


class StorageBaseSchema(BaseModel):
    """
    Базовая модель для хранения информации о хранилище.

    :param name: Название хранилища.
    :param location: Местоположение хранилища.
    :param capacity: Вместимость хранилища, представляемая как словарь.
                      Ключи типы отходов (например, "стекло", "пластик", "биоотходы"),
                      а значения — списки с уже помещенным количеством отходов и максимальной вместимостью.
    """

    name: str
    location: str
    capacity: Dict[str, list]


class StorageCreateSchema(StorageBaseSchema):
    """
    Модель для создания нового хранилища. Наследует от StorageBaseSchema.

    Используется при создании нового хранилища.
    """

    pass


class StorageSchema(StorageBaseSchema):
    """
    Модель для хранения информации о хранилище с его уникальным идентификатором.

    :param id: Уникальный идентификатор хранилища в базе данных.
    :param model_config: Конфигурация модели для автоматического извлечения значений атрибутов из ORM-модели.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
