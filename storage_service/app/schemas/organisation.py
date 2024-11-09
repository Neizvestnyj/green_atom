from pydantic import BaseModel


class OrganisationCopySchema(BaseModel):
    """
    Модель для хранения информации о копии организации.

    :param id: Уникальный идентификатор копии организации.
    """

    id: int
