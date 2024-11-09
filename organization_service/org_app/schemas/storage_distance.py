from pydantic import BaseModel


class StorageDistanceCopyBaseSchema(BaseModel):
    """
    Базовая модель для хранения копии данных о расстоянии между хранилищем и организацией.

    :param storage_id: Идентификатор хранилища
    :param organisation_id: Идентификатор организации
    :param distance: Расстояние между хранилищем и организацией
    """

    storage_id: int
    organisation_id: int
    distance: int


class StorageDistanceCopySchema(StorageDistanceCopyBaseSchema):
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
