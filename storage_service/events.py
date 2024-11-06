import asyncio
import json
from threading import Thread

import pika

from crud import create_organisation_copy, delete_organisation_by_id
from database import AsyncSessionLocal
from schemas import Storage


def send_storage_created_event(storage: Storage):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="storage_created")
    message = json.dumps({"id": storage.id, "capacity": storage.capacity})
    channel.basic_publish(exchange="", routing_key="storage_created", body=message)

    connection.close()


def send_storage_distance_created_event(storage_distance):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="storage_distance_created")
    message = json.dumps({
        "id": storage_distance.id,
        "storage_id": storage_distance.storage_id,
        "organisation_id": storage_distance.organisation_id,
        "distance": storage_distance.distance
    })
    channel.basic_publish(exchange="", routing_key="storage_distance_created", body=message)

    connection.close()


def listen_organisation_created_event():
    """Слушатель события создания новой организации."""
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="organisation_created")

    def callback(ch, method, properties, body):
        message = json.loads(body)
        organisation_id = message["id"]

        async def handle_event():
            async with AsyncSessionLocal() as db:  # Создаем копию организации
                await create_organisation_copy(db, organisation_id=organisation_id)

        asyncio.run(handle_event())

    channel.basic_consume(queue="organisation_created", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def listen_organisations_deleted_event():
    """Слушатель события удаления организации."""
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="organisations_delete")  # Создаем очередь для удаления организации

    def callback(ch, method, properties, body):
        message = json.loads(body)  # Словарь id-шников
        organisation_ids = message["id"]

        async def handle_event():
            async with AsyncSessionLocal() as db:
                for org_id in organisation_ids:
                    await delete_organisation_by_id(db, org_id)

        asyncio.run(handle_event())

    channel.basic_consume(queue="organisations_delete", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def start_listening_events():
    """Запуск прослушивания событий в отдельных потоках."""
    Thread(target=listen_organisation_created_event, daemon=True).start()
    Thread(target=listen_organisations_deleted_event, daemon=True).start()
