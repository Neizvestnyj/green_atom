from pydantic import BaseModel


class StorageDistanceBaseSchema(BaseModel):
    """
    Базовая модель для хранения информации о расстоянии между хранилищем и организацией.

    :param storage_id: Идентификатор хранилища.
    :param organisation_id: Идентификатор копии организации.
    :param distance: Расстояние между хранилищем и организацией (например, в километрах).
    """

    storage_id: int
    organisation_id: int
    distance: int


class StorageDistanceSchema(StorageDistanceBaseSchema):
    """
    Модель для хранения информации о расстоянии между хранилищем и организацией с уникальным идентификатором.

    :param id: Уникальный идентификатор записи о расстоянии.
    """

    id: int

    class Config:
        """
        Конфигурация модели Pydantic для StorageDistanceSchema.

        :from_attributes: Указывает, что модель может быть автоматически
        создана из атрибутов SQLAlchemy модели, например, при запросе
        из базы данных.
        """
        from_attributes = True
