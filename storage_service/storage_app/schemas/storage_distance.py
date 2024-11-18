from pydantic import BaseModel, ConfigDict


class StorageDistanceBaseSchema(BaseModel):
    """
    Базовая модель для хранения информации о расстоянии между хранилищем и организацией.

    :param storage_id: Идентификатор хранилища.
    :param organisation_id: Идентификатор копии организации.
    :param distance: Расстояние между хранилищем и организацией.
    """

    storage_id: int
    organisation_id: int
    distance: int


class StorageDistanceSchema(StorageDistanceBaseSchema):
    """
    Модель для хранения информации о расстоянии между хранилищем и организацией с уникальным идентификатором.

    :param model_config: Конфигурация модели для автоматического извлечения значений атрибутов из ORM-модели.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
