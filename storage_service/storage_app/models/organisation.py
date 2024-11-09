from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from . import Base


class OrganisationCopy(Base):
    """
    Модель для хранения информации о копиях организаций.
    Эта таблица используется для хранения связей между организациями и хранилищами.

    :param id: Уникальный идентификатор копии организации.
    :param storage_distances: Связь с таблицей расстояний (между хранилищем и организацией).
    """

    __tablename__ = "organisations_copy"

    id = Column(Integer, primary_key=True, index=True)
    storage_distances = relationship("StorageDistance",
                                     back_populates="organisation",
                                     cascade="all, delete-orphan",
                                     single_parent=True,
                                     )
