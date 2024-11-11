from typing import Dict

from pydantic import BaseModel


class RecycleRequestSchema(BaseModel):
    """
    Модель запроса на утилизацию отходов.

    :param organisation_id: Идентификатор организации, запрашивающей утилизацию
    """

    organisation_id: int


class RecycleResponseSchema(BaseModel):
    """
    Модель ответа на запрос утилизации, содержащая план утилизации по хранилищам.

    :param storage_plan: Словарь, содержащий ID хранилища и объемы отходов, которые
                         можно туда передать.
                         Пример: {1: {"Стекло": 50, "Биоотходы": 100}, 2: {"Стекло": 50}}
    :param message: Сообщение о статусе переработки
    """

    storage_plan: Dict[int, Dict[str, int]]
    message: str
