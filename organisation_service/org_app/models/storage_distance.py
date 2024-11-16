from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class StorageDistanceCopy(Base):
    """
    Модель для хранения копий расстояний между хранилищами и организациями.

    :param id: Уникальный идентификатор копии расстояния
    :param storage_id: Идентификатор хранилища (внешний ключ на таблицу storage_copies)
    :param organisation_id: Идентификатор организации (внешний ключ на таблицу organisations)
    :param distance: Расстояние между хранилищем и организацией
    :param storage: Связь с таблицей копий хранилищ
    :param organisation: Связь с таблицей организаций
    """

    __tablename__ = "storage_distances_copy"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storages_copy.id"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    distance = Column(Integer, nullable=False)

    # Уникальное ограничение
    __table_args__ = (
        UniqueConstraint('storage_id', 'organisation_id', 'distance', name='uq_storage_organisation_distance'),
    )

    # Связь с таблицей копий хранилищ и организаций
    storage = relationship("StorageCopy", back_populates="storage_distances_copy")
    organisation = relationship("Organisation", back_populates="storage_distances_copy")
