import json
from typing import Sequence

import pika

from org_app.models.organisation import Organisation
from org_app.events import RABBITMQ_HOST


def send_organisation_created_event(organisation: Organisation) -> None:
    """
    Отправка события о создании организации в очередь RabbitMQ.

    :param organisation: объект организации, данные которой отправляются в очередь
    :return: None

    Функция отправляет сообщение с ID организации в очередь organisation_created
    для дальнейшей обработки другими сервисами или компонентами системы.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="organisation_created")
    message = json.dumps({"id": organisation.id})
    channel.basic_publish(exchange="", routing_key="organisation_created", body=message)

    connection.close()


def send_organisations_delete_event(organisations: Sequence[Organisation]) -> None:
    """
    Отправка события об удалении организаций в очередь RabbitMQ.

    :param organisations: список объектов организаций, данные которых отправляются в очередь
    :return: None

    Функция формирует и отправляет сообщение с ID удалённых организаций в очередь organisations_delete,
    чтобы другие компоненты могли обработать это событие для синхронизации данных.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="organisations_delete")

    organisations_data = {"id": [org.id for org in organisations]}
    message = json.dumps(organisations_data)

    channel.basic_publish(
        exchange="",
        routing_key="organisations_delete",
        body=message,
    )

    connection.close()
