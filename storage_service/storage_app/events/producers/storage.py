import json

import pika

from storage_app.events import RABBITMQ_HOST
from storage_app.models.storage import Storage


def send_storage_created_event(storage: Storage) -> None:
    """
    Отправка события о создании нового хранилища.

    :param storage: Объект хранилища, для которого отправляется событие
    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="storage_created")
    message = json.dumps({"id": storage.id, "capacity": storage.capacity})
    channel.basic_publish(exchange="", routing_key="storage_created", body=message)

    connection.close()
