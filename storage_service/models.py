from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Storage(Base):
    __tablename__ = "storages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String, nullable=False)
    capacity = Column(JSON, nullable=False)  # Стекло, пластик и т.д.


class OrganisationCopy(Base):
    __tablename__ = "organisation_copies"

    id = Column(Integer, primary_key=True, index=True)
    storage_distances = relationship("StorageDistance", back_populates="organisation", cascade="all, delete-orphan",
                                     single_parent=True,
                                     )


class StorageDistance(Base):
    __tablename__ = "storage_distances"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storages.id"))
    organisation_id = Column(Integer, ForeignKey("organisation_copies.id"))
    distance = Column(Float, nullable=False)

    storage = relationship("Storage")
    organisation = relationship("OrganisationCopy")
