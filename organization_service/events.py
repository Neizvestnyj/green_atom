import asyncio
import json
from threading import Thread

import pika

from crud import create_storage_copy, create_storage_distance_copy
from database import AsyncSessionLocal
from schemas import Organisation


def send_organisation_created_event(organisation: Organisation) -> None:
    """
    Отправка события о создании организации в очередь RabbitMQ.

    :param organisation: объект организации, данные которой отправляются в очередь
    :return: None

    Функция отправляет сообщение с ID организации в очередь `organisation_created`
    для дальнейшей обработки другими сервисами или компонентами системы.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="organisation_created")
    message = json.dumps({"id": organisation.id})
    channel.basic_publish(exchange="", routing_key="organisation_created", body=message)

    connection.close()


def send_organisations_delete_event(organisations: list[Organisation]) -> None:
    """
    Отправка события об удалении организаций в очередь RabbitMQ.

    :param organisations: список объектов организаций, данные которых отправляются в очередь
    :return: None

    Функция формирует и отправляет сообщение с ID удалённых организаций в очередь `organisations_delete`,
    чтобы другие компоненты могли обработать это событие, например, для синхронизации данных.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
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


def listen_storage_created_event() -> None:
    """
    Прослушивание очереди `storage_created` для получения события о создании хранилища.

    :return: None

    Функция прослушивает очередь `storage_created` и, получив сообщение, извлекает данные о хранилище,
    затем создает копию хранилища в базе данных с помощью функции `create_storage_copy`.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="storage_created")

    def callback(ch, method, properties, body):
        """
        Обработчик событий, который вызывает создание копии хранилища.

        :param ch: канал связи с RabbitMQ
        :param method: информация о доставке сообщения
        :param properties: дополнительные свойства сообщения
        :param body: данные события в виде байт
        :return: None

        Функция извлекает данные из события, а затем инициирует асинхронную обработку.
        """

        message = json.loads(body)
        storage_id = message["id"]
        capacity = message["capacity"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                # Создаем копию хранилища
                await create_storage_copy(db, storage_id=storage_id, capacity=capacity)

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def listen_storage_distance_created_event() -> None:
    """
    Прослушивание очереди `storage_distance_created` для получения события о создании расстояния между хранилищем и организацией.

    :return: None

    Функция прослушивает очередь `storage_distance_created` и, получив сообщение, извлекает данные о расстоянии,
    затем создает копию записи о расстоянии в базе данных с помощью функции `create_storage_distance_copy`.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="storage_distance_created")

    def callback(ch, method, properties, body):
        """
        Обработчик событий, который вызывает создание копии записи о расстоянии между хранилищем и организацией.

        :param ch: канал связи с RabbitMQ
        :param method: информация о доставке сообщения
        :param properties: дополнительные свойства сообщения
        :param body: данные события в виде байт
        :return: None

        Функция извлекает данные из события и инициирует асинхронную обработку.
        """

        message = json.loads(body)
        storage_distance_id = message["id"]
        storage_id = message["storage_id"]
        organisation_id = message["organisation_id"]
        distance = message["distance"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                # Создаем копию записи о расстоянии
                await create_storage_distance_copy(db,
                                                   storage_distance_id=storage_distance_id,
                                                   storage_id=storage_id,
                                                   organisation_id=organisation_id,
                                                   distance=distance,
                                                   )

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_distance_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def start_listening_events() -> None:
    """
    Запуск прослушивания событий в отдельных потоках.

    :return: None

    Функция запускает прослушивание двух событий: о создании хранилища и о создании расстояния.
    Для каждого события используется отдельный поток, что позволяет асинхронно обрабатывать события.
    """

    Thread(target=listen_storage_created_event, daemon=True).start()
    Thread(target=listen_storage_distance_created_event, daemon=True).start()
