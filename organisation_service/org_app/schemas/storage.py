from typing import Dict

from pydantic import BaseModel, ConfigDict


class StorageCopyBaseSchema(BaseModel):
    """
    Базовая модель для хранения копии данных хранилища.

    :param capacity: Словарь, где ключ - это тип отходов, а значение - список с заполненной и свободной ёмкостью хранилища
    """

    capacity: Dict[str, list]


class StorageCopySchema(StorageCopyBaseSchema):
    """
    Модель копии хранилища с ID. Представляет копию данных хранилища в базе данных.

    :param id: Уникальный идентификатор копии хранилища
    :param capacity: Словарь типов отходов и их ёмкостей в хранилище
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
