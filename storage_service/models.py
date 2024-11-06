from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Storage(Base):
    """
    Модель для хранения информации о хранилищах (складах).

    :param id: Уникальный идентификатор хранилища.
    :param name: Название хранилища.
    :param location: Местоположение хранилища.
    :param capacity: Вместимость хранилища, хранимая в виде JSON (например, типы материалов и их количество).
    """

    __tablename__ = "storages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String, nullable=False)
    capacity = Column(JSON, nullable=False)  # Например, стекло, пластик и т.д.


class OrganisationCopy(Base):
    """
    Модель для хранения информации о копиях организаций.
    Эта таблица используется для хранения связей между организациями и хранилищами.

    :param id: Уникальный идентификатор копии организации.
    :param storage_distances: Связь с таблицей расстояний (между хранилищем и организацией).
    """

    __tablename__ = "organisation_copies"

    id = Column(Integer, primary_key=True, index=True)
    storage_distances = relationship("StorageDistance",
                                     back_populates="organisation",
                                     cascade="all, delete-orphan",
                                     single_parent=True,
                                     )


class StorageDistance(Base):
    """
    Модель для хранения информации о расстоянии между хранилищем и организацией.

    :param id: Уникальный идентификатор записи о расстоянии.
    :param storage_id: Идентификатор хранилища (ссылается на `storages.id`).
    :param organisation_id: Идентификатор копии организации (ссылается на `organisation_copies.id`).
    :param distance: Расстояние между хранилищем и организацией (например, в километрах).
    :param storage: Связь с таблицей `Storage` (хранилище).
    :param organisation: Связь с таблицей `OrganisationCopy` (копия организации).
    """

    __tablename__ = "storage_distances"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storages.id"))
    organisation_id = Column(Integer, ForeignKey("organisation_copies.id"))
    distance = Column(Float, nullable=False)

    # Определение связей с другими таблицами
    storage = relationship("Storage", back_populates="storage_distances")
    organisation = relationship("OrganisationCopy", back_populates="storage_distances")
