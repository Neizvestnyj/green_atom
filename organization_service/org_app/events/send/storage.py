import json
from typing import Dict

import pika

from org_app.events import RABBITMQ_HOST


def send_update_capacity_event(storage_id: int, updated_capacity: Dict[str, int]) -> None:
    """
    Отправка события об обновлении емкости хранилища в очередь RabbitMQ.

    :param storage_id: Идентификатор хранилища
    :param updated_capacity: Словарь с обновленной емкостью для различных типов отходов
    :return: None

    Функция отправляет сообщение с ID хранилища и его обновленной емкостью в очередь "update_capacity"
    для дальнейшей обработки другим сервисом.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="update_capacity")

    message = json.dumps({
        "storage_id": storage_id,
        "updated_capacity": updated_capacity  # Например, {"Пластик": 10, "Биоотходы": 50}
    })

    channel.basic_publish(exchange="", routing_key="update_capacity", body=message)

    connection.close()
