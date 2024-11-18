import json

import pika

from storage_app.events import RABBITMQ_HOST
from storage_app.models.storage_distance import StorageDistance


def send_storage_distance_created_event(storage_distance: StorageDistance) -> None:
    """
    Отправка события о создании нового расстояния между хранилищем и организацией.

    :param storage_distance: Объект расстояния между хранилищем и организацией
    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="storage_distance_created")
    message = json.dumps({
        "id": storage_distance.id,
        "storage_id": storage_distance.storage_id,
        "organisation_id": storage_distance.organisation_id,
        "distance": storage_distance.distance,
    })
    channel.basic_publish(exchange="", routing_key="storage_distance_created", body=message)

    connection.close()

def send_distance_deleted_event(sotrage_distance: StorageDistance) -> None:
    """
    Отправка события об удалении расстояния.

    :param sotrage_distance: Объект расстояния, для которого отправляется событие
    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="distance_delete")
    message = json.dumps({"id": sotrage_distance.id})
    channel.basic_publish(exchange="",
                          routing_key="distance_delete",
                          body=message,
                          )

    connection.close()
