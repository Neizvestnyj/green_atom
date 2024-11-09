import asyncio
import json

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from organization_service.app.crud.storage_distance import create_storage_distance_copy
from organization_service.app.database import AsyncSessionLocal


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

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
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
