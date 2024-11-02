"""
`channel.queue_declare`
Очередь используется для гарантированной доставки сообщений между микросервисами, особенно когда они работают асинхронно.
Например, при создании организации событие отправляется в очередь organization_created, где оно может быть обработано потребителями,
даже если они временно недоступны. Очереди обеспечивают надежность (сообщения не теряются) и независимость между сервисами,
позволяя им обмениваться данными, не вызывая друг друга напрямую.
"""
import threading

import pika
from fastapi import FastAPI, HTTPException
from models import Organization, WasteType, WasteUpdate
from typing import List
import os
import logging
import json

logger = logging.getLogger(__name__)

app = FastAPI()

# RabbitMQ connection parameters
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')

# Хранилище для организаций
organizations = []

# Настройка RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue='organization_created')
channel.queue_declare(queue='organization_updated')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    message = json.loads(body)
    organization_id = message['organization_id']
    waste_type = message['waste_type']
    amount = message['amount']

    # Найти организацию
    organization = next((org for org in organizations if org.id == organization_id), None)
    if organization:
        organization.add_waste(waste_type, -amount)  # Уменьшаем количество отходов в организации
        print(f"Уменьшено количество {waste_type} в организации {organization.name} на {amount}.")
    else:
        logger.error(f"Организация с ID {organization_id} не найдена.")


# Установка обработки сообщений
channel.basic_consume(queue='waste_transfer', on_message_callback=callback, auto_ack=True)


@app.post("/organizations/", response_model=Organization)
async def create_organization(organization: Organization):
    print('Created')
    # Проверка, что типы отходов допустимы
    valid_waste_types = {waste.value for waste in WasteType}
    if not all(waste in valid_waste_types for waste in organization.waste_quantities.keys()):
        raise HTTPException(status_code=400, detail="Invalid waste type(s) provided.")

    # Генерация уникального идентификатора для новой организации
    organizations.append(organization)

    # Отправка сообщения в RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key='organization_created',
        body=f"Создана новая организация: {organization.name}, отходы: {organization.waste_quantities}"
    )

    return organization


@app.put("/organizations/{org_id}", response_model=Organization)
async def update_organization(org_id: int, waste_update: WasteUpdate):
    logger.debug(f"Current organizations: {organizations}")
    for org in organizations:
        logger.debug(f"Checking organization ID: {org.id} against {org_id}")

    org = next((org for org in organizations if org.id == org_id), None)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found.")

    # Update the waste quantities
    for waste_type, quantity in waste_update.waste_quantities.items():
        org.waste_quantities[waste_type] = quantity

    channel.basic_publish(
        exchange='',
        routing_key='organization_updated',
        body=f"Обновлено количество отходов для организации: {org.name}, отходы: {org.waste_quantities}"
    )

    return org


@app.get("/organizations/", response_model=List[Organization])
async def get_organizations():
    return organizations


@app.get("/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: int):
    org = next((org for org in organizations if org.id == org_id), None)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return org


# Функция для запуска RabbitMQ consumer в отдельном потоке
def start_rabbitmq_consumer():
    print("Starting RabbitMQ consumer...")
    channel.start_consuming()


@app.on_event("startup")
async def startup_event():
    # Запускаем consumer в фоновом потоке при старте приложения
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    consumer_thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    global connection
    if connection:
        connection.close()  # Закрываем соединение при завершении работы приложения


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=5000, log_level="debug")
