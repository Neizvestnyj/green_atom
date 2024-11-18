from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from . import Base


class Storage(Base):
    """
    Модель для хранения информации о хранилищах (складах).

    :param id: Уникальный идентификатор хранилища.
    :param name: Название хранилища.
    :param location: Местоположение хранилища.
    :param capacity: Вместимость хранилища, хранимая в виде JSON (типы отходов и их количество).
    :param storage_distances: Связь с таблицей расстояний
    """

    __tablename__ = "storages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String, nullable=False)
    capacity = Column(JSON, nullable=False)

    storage_distances = relationship("StorageDistance",
                                     back_populates="storage",
                                     cascade="all, delete-orphan",
                                     single_parent=True,
                                     )
