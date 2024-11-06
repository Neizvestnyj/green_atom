from typing import Dict

from pydantic import BaseModel


class OrganisationBase(BaseModel):
    name: str
    capacity: Dict[str, list]


class OrganisationCreate(OrganisationBase):
    pass


class Organisation(OrganisationBase):
    id: int

    class Config:
        from_attributes = True


class StorageCopyBase(BaseModel):
    capacity: Dict[str, list]


class StorageCopy(StorageCopyBase):
    id: int

    class Config:
        from_attributes = True


class StorageDistanceCopyBase(BaseModel):
    storage_id: int
    organisation_id: int
    distance: float


class StorageDistanceCopy(StorageDistanceCopyBase):
    id: int

    class Config:
        from_attributes = True
