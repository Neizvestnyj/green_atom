from typing import Dict

from pydantic import BaseModel, ConfigDict


class OrganisationBaseSchema(BaseModel):
    """
    Базовая модель для организации.

    :param name: Название организации
    :param capacity: Словарь, где ключ - это тип ресурса (например, стекло, пластик), а значение - список ёмкостей
    """

    name: str
    capacity: Dict[str, list]


class OrganisationCreateSchema(OrganisationBaseSchema):
    """
    Модель для создания организации. Наследует от `OrganisationBase` и используется для создания новых записей.
    """

    pass


class OrganisationSchema(OrganisationBaseSchema):
    """
    Модель организации с ID. Используется для представления организации после её создания.

    :param id: Уникальный идентификатор организации
    :param name: Название организации
    :param capacity: Словарь типов отходов и их ёмкостей
    :param model_config: Конфигурация модели для автоматического извлечения значений атрибутов из ORM-модели.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)  # Включает возможность создания модели из атрибутов объекта
