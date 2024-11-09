from typing import Dict

from pydantic import BaseModel


class StorageSchemaCopyBaseSchema(BaseModel):
    """
    Базовая модель для хранения копии данных хранилища.

    :param capacity: Словарь, где ключ - это тип ресурса, а значение - список ёмкостей хранилища
    """

    capacity: Dict[str, list]


class StorageSchemaCopySchema(StorageSchemaCopyBaseSchema):
    """
    Модель копии хранилища с ID. Представляет копию данных хранилища в базе данных.

    :param id: Уникальный идентификатор копии хранилища
    :param capacity: Словарь типов ресурсов и их ёмкостей в хранилище
    """

    id: int

    class Config:
        from_attributes = True
