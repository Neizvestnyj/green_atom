import asyncio
import json

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from org_app.crud.storage import create_storage_copy
from org_app.database import AsyncSessionLocal
from org_app.events import RABBITMQ_HOST
from org_app.schemas.storage import StorageCopySchema


def listen_storage_created_event() -> None:
    """
    Прослушивание очереди `storage_created` для получения события о создании хранилища.

    :return: None

    Функция прослушивает очередь `storage_created` и, получив сообщение, извлекает данные о хранилище,
    затем создает копию хранилища в базе данных с помощью функции `create_storage_copy`.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="storage_created")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
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
                storage_copy_data = StorageCopySchema(id=storage_id, capacity=capacity)
                await create_storage_copy(db, storage=storage_copy_data)

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
