from sqlalchemy import Column, Integer, JSON
from sqlalchemy.orm import relationship

from . import Base


class StorageCopy(Base):
    """
    Модель для хранения копий данных о хранилищах.

    :param id: Уникальный идентификатор копии хранилища
    :param capacity: Структура данных, описывающая ёмкость хранилища
    :param storage_distances_copy: Связь с таблицей расстояний
    """

    __tablename__ = "storages_copy"

    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(JSON, nullable=False)  # Копия данных из сервиса Хранилище

    storage_distances_copy = relationship("StorageDistanceCopy",
                                          back_populates="storage",
                                          cascade="all, delete-orphan",
                                          single_parent=True,
                                          )
