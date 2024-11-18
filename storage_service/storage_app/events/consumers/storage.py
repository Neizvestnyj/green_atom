import asyncio
import json

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from storage_app.crud.storage import update_storage_capacity as crud_update_storage_capacity
from storage_app.database import AsyncSessionLocal
from storage_app.events import RABBITMQ_HOST


def listen_storage_capacity_event() -> None:
    """
    Запускаем слушатель для обработки сообщений из очереди RabbitMQ и обновления хранилища.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="update_capacity")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """
        Обработчик сообщений из очереди, который создает копию организации.

        :param ch: Канал RabbitMQ
        :param method: Метаданные о сообщении
        :param properties: Свойства сообщения
        :param body: Тело сообщения, содержащее id организации и новые данные о заполнении хранилища
        :return: None
        """

        message = json.loads(body)
        storage_id = message.get("storage_id")
        updated_capacity = message.get("updated_capacity")

        if storage_id and updated_capacity:
            async def handle_event():
                async with AsyncSessionLocal() as db:
                    await crud_update_storage_capacity(db, storage_id, updated_capacity)

            asyncio.run(handle_event())

    channel.basic_consume(queue="update_capacity", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
