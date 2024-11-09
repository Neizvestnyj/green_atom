from threading import Thread

from .organisation import listen_organisation_created_event, listen_organisations_deleted_event


def start_listening_events() -> None:
    """
    Запускает прослушивание событий о создании и удалении организаций в отдельных потоках.

    :return: None
    """

    Thread(target=listen_organisation_created_event, daemon=True).start()
    Thread(target=listen_organisations_deleted_event, daemon=True).start()
