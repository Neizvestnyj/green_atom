from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Базовый класс для определения моделей
Base = declarative_base()


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
    capacity = Column(JSON, nullable=False)  # Стекло, пластик и т.д.

    # Связь с таблицей копий расстояний
    storage_distances_copy = relationship(
        "StorageDistanceCopy",
        back_populates="organisation",  # Имя переменной на стороне StorageDistanceCopy
        cascade="all, delete-orphan",  # Удаление зависимых объектов при удалении организации
        single_parent=True,  # Ограничивает создание только одного родительского объекта
    )


class StorageCopy(Base):
    """
    Модель для хранения копий данных о хранилищах.

    :param id: Уникальный идентификатор копии хранилища
    :param capacity: Структура данных, описывающая ёмкость хранилища
    :param storage_distances: Связь с таблицей расстояний
    """

    __tablename__ = "storage_copies"

    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(JSON, nullable=False)  # Копия данных из сервиса Хранилище

    storage_distances = relationship("StorageDistanceCopy",
                                     back_populates="storage",
                                     cascade="all, delete-orphan",
                                     single_parent=True,
                                     )


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

    __tablename__ = "storage_distance_copies"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(Integer, ForeignKey("storage_copies.id"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    distance = Column(Float, nullable=False)

    # Связь с таблицей копий хранилищ
    storage = relationship("StorageCopy")

    # Связь с таблицей организаций
    organisation = relationship("Organisation")
