"""
Сервис Организаций
"""

from pydantic import BaseModel
from typing import Dict
from enum import Enum


# Модель типа отхода
class WasteType(str, Enum):
    bio = "биоотходы"  # Bio waste
    glass = "стекло"  # Glass
    plastic = "пластик"  # Plastic


class WasteUpdate(BaseModel):
    waste_quantities: Dict[WasteType, int]


class Organization(BaseModel):
    id: int
    name: str
    waste_quantities: Dict[WasteType, int]  # Словарь с типами отходов и их количеством

    def add_waste(self, waste_type: str, amount: int):
        if waste_type in self.waste_quantities:
            self.waste_quantities[waste_type] += amount
        else:
            self.waste_quantities[waste_type] = amount

    class Config:
        arbitrary_types_allowed = True
