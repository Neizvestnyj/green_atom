from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from . import Base


class Organisation(Base):
    """
    Модель для представления организации в базе данных.

    :param id: Уникальный идентификатор организации
    :param name: Название организации (уникальное)
    :param capacity: Структура данных, описывающая ёмкость (например, стекло, пластик и т.д.)
    :param storage_distances_copy: Связь с таблицей копий расстояний между хранилищами и организациями
    """

    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    capacity = Column(JSON, nullable=False)  # Стекло, пластик, биоотходы

    # Связь с таблицей копий расстояний
    storage_distances_copy = relationship(
        "StorageDistanceCopy",
        back_populates="organisation",  # Имя переменной на стороне StorageDistanceCopySchema
        cascade="all, delete-orphan",  # Удаление зависимых объектов при удалении организации
        single_parent=True,  # Ограничивает создание только одного родительского объекта
    )
