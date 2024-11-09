import json

import pika

from storage_service.app.models.storage_distance import StorageDistance


def send_storage_distance_created_event(storage_distance: StorageDistance) -> None:
    """
    Отправка события о создании нового расстояния между хранилищем и организацией.

    :param storage_distance: Объект расстояния между хранилищем и организацией
    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
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
