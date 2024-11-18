from threading import Thread

from .storage import listen_storage_created_event, listen_storage_deleted_event
from .storage_distance import listen_storage_distance_created_event


def start_listening_events() -> None:
    """
    Запуск прослушивания событий в отдельных потоках.

    :return: None

    Функция запускает прослушивание двух событий: о создании хранилища и о создании расстояния.
    Для каждого события используется отдельный поток, что позволяет асинхронно обрабатывать события.
    """

    Thread(target=listen_storage_created_event, daemon=True).start()
    Thread(target=listen_storage_deleted_event, daemon=True).start()

    Thread(target=listen_storage_distance_created_event, daemon=True).start()
