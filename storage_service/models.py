from pydantic import BaseModel
from typing import Dict
from enum import Enum


# Модель типа отхода
class WasteType(str, Enum):
    bio = "биоотходы"  # Bio waste
    glass = "стекло"  # Glass
    plastic = "пластик"  # Plastic

class WasteTransferRequest(BaseModel):
    organization_id: int
    storage_id: int
    waste_type: str
    amount: int


class Storage(BaseModel):
    id: int
    location: str
    max_capacity: Dict[WasteType, int]
    current_storage: Dict[WasteType, int]

    def can_accept(self, waste_type: WasteType, amount: int) -> bool:
        return (self.current_storage[waste_type] + amount) <= self.max_capacity[waste_type]

    def add_waste(self, waste_type: WasteType, amount: int):
        if self.can_accept(waste_type, amount):
            self.current_storage[waste_type] += amount
        else:
            raise ValueError("Максимальный запас в хранилище превышен")
