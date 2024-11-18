from threading import Thread

from .organisation import listen_organisation_created_event, listen_organisation_deleted_event
from .storage import listen_storage_capacity_event


def start_listening_events() -> None:
    """
    Запускает прослушивание событий о создании и удалении организаций в отдельных потоках.

    :return: None
    """

    Thread(target=listen_organisation_created_event, daemon=True).start()
    Thread(target=listen_organisation_deleted_event, daemon=True).start()
    Thread(target=listen_storage_capacity_event, daemon=True).start()
