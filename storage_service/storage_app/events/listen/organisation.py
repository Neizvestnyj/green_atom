import asyncio
import json

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from storage_app.crud.organisation import create_organisation_copy, delete_organisation_by_id
from storage_app.database import AsyncSessionLocal
from storage_app.events import RABBITMQ_HOST


def listen_organisation_created_event() -> None:
    """
    Слушатель события создания новой организации. Создает копию организации при получении события.

    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="organisation_created")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        """
        Обработчик сообщений из очереди, который создает копию организации.

        :param ch: Канал RabbitMQ
        :param method: Метаданные о сообщении
        :param properties: Свойства сообщения
        :param body: Тело сообщения, содержащее id организации
        :return: None
        """

        message = json.loads(body)
        organisation_id = message["id"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                await create_organisation_copy(db, organisation_id=organisation_id)

        asyncio.run(handle_event())

    channel.basic_consume(queue="organisation_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def listen_organisations_deleted_event() -> None:
    """
    Слушатель события удаления организации. Удаляет организации по полученному списку id.

    :return: None
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="organisations_delete")

    def callback(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        """
        Обработчик сообщений из очереди, который удаляет организации по id.

        :param ch: Канал RabbitMQ
        :param method: Метаданные о сообщении
        :param properties: Свойства сообщения
        :param body: Тело сообщения, содержащее список id организаций для удаления
        :return: None
        """

        message = json.loads(body)
        organisation_ids = message["id"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                for org_id in organisation_ids:
                    await delete_organisation_by_id(db, org_id)

        asyncio.run(handle_event())

    channel.basic_consume(queue="organisations_delete", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
