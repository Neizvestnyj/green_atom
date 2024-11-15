from pydantic import BaseModel, ConfigDict


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
    :param model_config: Конфигурация модели для автоматического извлечения значений атрибутов из ORM-модели.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
