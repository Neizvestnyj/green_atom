import asyncio
import json
from threading import Thread

import pika

from crud import create_storage_copy, create_storage_distance_copy
from database import AsyncSessionLocal
from schemas import Organisation


def send_organisation_created_event(organisation: Organisation):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="organisation_created")
    message = json.dumps({"id": organisation.id})
    channel.basic_publish(exchange="", routing_key="organisation_created", body=message)

    connection.close()


def send_organisations_delete_event(organisations: list[Organisation]):
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Обеспечиваем наличие очереди
    channel.queue_declare(queue="organisations_delete")

    # Подготовка сообщения с данными удалённых организаций
    organisations_data = {"id": [org.id for org in organisations]}
    message = json.dumps(organisations_data)

    # Отправка сообщения
    channel.basic_publish(
        exchange="",
        routing_key="organisations_delete",
        body=message,
    )
    print(f" [x] Sent 'Organisations Deleted' event with {len(organisations)} organisations with message {message}")

    # Закрытие подключения
    connection.close()


def listen_storage_created_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="storage_created")

    def callback(ch, method, properties, body):
        message = json.loads(body)
        storage_id = message["id"]
        capacity = message["capacity"]

        async def handle_event():
            async with AsyncSessionLocal() as db:  # Создаем копию хранилища
                await create_storage_copy(db, storage_id=storage_id, capacity=capacity)

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def listen_storage_distance_created_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="storage_distance_created")

    def callback(ch, method, properties, body):
        message = json.loads(body)
        storage_distance_id = message["id"]
        storage_id = message["storage_id"]
        organisation_id = message["organisation_id"]
        distance = message["distance"]

        async def handle_event():
            async with AsyncSessionLocal() as db:  # Создаем копию расстояния
                await create_storage_distance_copy(db,
                                                   storage_distance_id=storage_distance_id,
                                                   storage_id=storage_id,
                                                   organisation_id=organisation_id,
                                                   distance=distance,
                                                   )

        asyncio.run(handle_event())

    channel.basic_consume(queue="storage_distance_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def start_listening_events():
    """Запуск прослушивания событий в отдельных потоках."""
    Thread(target=listen_storage_created_event, daemon=True).start()
    Thread(target=listen_storage_distance_created_event, daemon=True).start()
