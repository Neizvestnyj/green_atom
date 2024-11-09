from typing import Dict

from pydantic import BaseModel


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
