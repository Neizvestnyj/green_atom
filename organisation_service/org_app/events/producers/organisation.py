import json

import pika

from org_app.events import RABBITMQ_HOST
from org_app.models.organisation import Organisation


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


def send_organisation_delete_event(organisation: Organisation) -> None:
    """
    Отправка события об удалении организаций в очередь RabbitMQ.

    :param organisation: объект организации, данные которой отправляются в очередь
    :return: None

    Функция формирует и отправляет сообщение с ID удалённой организации в очередь organisations_delete,
    чтобы другие компоненты могли обработать это событие для синхронизации данных.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="organisation_delete")

    organisations_data = {"id": organisation.id}
    message = json.dumps(organisations_data)

    channel.basic_publish(
        exchange="",
        routing_key="organisation_delete",
        body=message,
    )

    connection.close()
