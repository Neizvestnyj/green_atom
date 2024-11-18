from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class StorageDistance(Base):
    """
    Модель для хранения информации о расстоянии между хранилищем и организацией.

    :param id: Уникальный идентификатор записи о расстоянии.
    :param storage_id: Идентификатор хранилища (ссылается на `storages.id`).
    :param organisation_id: Идентификатор копии организации (ссылается на `organisations_copy.id`).
    :param distance: Расстояние между хранилищем и организацией.
    :param storage: Связь с таблицей `Storage` (хранилище).
    :param organisation: Связь с таблицей `OrganisationCopy` (копия организации).
    """

    __tablename__ = "storage_distances"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storages.id"))
    organisation_id = Column(Integer, ForeignKey("organisations_copy.id"))
    distance = Column(Integer, nullable=False)

    # Уникальное ограничение
    __table_args__ = (
        UniqueConstraint('storage_id', 'organisation_id', 'distance', name='uq_storage_organisation_distance'),
    )

    # Определение связей с другими таблицами
    storage = relationship("Storage", back_populates="storage_distances")
    organisation = relationship("OrganisationCopy", back_populates="storage_distances")
