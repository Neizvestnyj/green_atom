from typing import Dict

from pydantic import BaseModel


class StorageBase(BaseModel):
    name: str
    location: str
    capacity: Dict[str, list]


class StorageCreate(StorageBase):
    pass


class Storage(StorageBase):
    id: int

    class Config:
        from_attributes = True


class OrganisationCopy(BaseModel):
    id: int


class StorageDistanceBase(BaseModel):
    storage_id: int
    organisation_id: int
    distance: float


class StorageDistance(StorageDistanceBase):
    id: int

    class Config:
        from_attributes = True
