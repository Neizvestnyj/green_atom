from threading import Thread

from .storage import listen_storage_created_event, listen_storage_deleted_event
from .storage_distance import listen_storage_distance_created_event, listen_distance_deleted_event


def start_listening_events() -> None:
    """
    Запуск прослушивания событий в отдельных потоках.

    :return: None

    Функция запускает прослушивание событий: о создании/удалении хранилища и о создании/удалении расстояния.
    """

    Thread(target=listen_storage_created_event, daemon=True).start()
    Thread(target=listen_storage_deleted_event, daemon=True).start()

    Thread(target=listen_storage_distance_created_event, daemon=True).start()
    Thread(target=listen_distance_deleted_event, daemon=True).start()
