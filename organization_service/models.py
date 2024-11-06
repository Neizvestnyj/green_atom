from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    capacity = Column(JSON, nullable=False)  # Стекло, пластик и т.д.


class StorageCopy(Base):
    __tablename__ = "storage_copies"

    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(JSON, nullable=False)  # Копия данных из сервиса Хранилище


class StorageDistanceCopy(Base):
    __tablename__ = "storage_distance_copies"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storage_copies.id"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    distance = Column(Float, nullable=False)

    storage = relationship("StorageCopy")
    organisation = relationship("Organisation")
