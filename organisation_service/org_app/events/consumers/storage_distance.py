import asyncio
import json

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from org_app.crud.storage_distance import create_storage_distance_copy, delete_distance
from org_app.database import AsyncSessionLocal
from org_app.events import RABBITMQ_HOST
from org_app.schemas.storage_distance import StorageDistanceCopySchema


def listen_storage_distance_created_event() -> None:
    """
    Прослушивание очереди `storage_distance_created` для получения события о создании расстояния между хранилищем и организацией.

    :return: None

    Функция прослушивает очередь `storage_distance_created` и, получив сообщение, извлекает данные о расстоянии,
    затем создает копию записи о расстоянии в базе данных с помощью функции `create_storage_distance_copy`.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="storage_distance_created")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
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
                storage_distance_data = StorageDistanceCopySchema(id=storage_distance_id,
                                                                  storage_id=storage_id,
                                                                  organisation_id=organisation_id,
                                                                  distance=distance,
                                                                  )
                await create_storage_distance_copy(db,
                                                   storage_distance=storage_distance_data,
                                                   )

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_distance_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def listen_distance_deleted_event() -> None:
    """
    Слушатель события удаления расстояния. Удаляет расстояние по полученному id.

    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="distance_delete")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """
        Обработчик сообщений из очереди, который удаляет организации по id.

        :param ch: Канал RabbitMQ
        :param method: Метаданные о сообщении
        :param properties: Свойства сообщения
        :param body: Тело сообщения, содержащее список id организаций для удаления
        :return: None
        """

        message = json.loads(body)
        distance_id = message["id"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                await delete_distance(db, distance_id)

        asyncio.run(handle_event())

    channel.basic_consume(queue="distance_delete", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
