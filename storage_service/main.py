import json
import os
from fastapi import FastAPI, HTTPException
from models import Storage, WasteTransferRequest
import os
import pika
from fastapi import FastAPI
from typing import List, Dict, Any

app = FastAPI()

# RabbitMQ connection parameters
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare a queue for waste transfer
channel.queue_declare(queue='waste_transfer')

# In-memory storage for demonstration
storages = []


@app.post("/storages/", response_model=Storage)
def create_storage(storage: Storage):
    storages.append(storage)
    return storage


@app.post("/transfer/")
def transfer_waste(request: WasteTransferRequest):
    storage = next((sto for sto in storages if sto.id == request.storage_id), None)

    if storage:
        try:
            storage.add_waste(request.waste_type, request.amount)

            # Publish a message to RabbitMQ
            message = {
                "organization_id": request.organization_id,
                "storage_id": storage.id,
                "waste_type": request.waste_type,
                "amount": request.amount
            }
            channel.basic_publish(exchange='', routing_key='waste_transfer', body=json.dumps(message))

            return {"status": "success", "message": f"Отходы добавлены в хранилище {storage.location}"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "Хранилище не найдено"}


@app.get("/storages/", response_model=List[Storage])
def get_storages():
    if not storages:
        raise HTTPException(status_code=404, detail="Нет хранилищ.")

    return storages

@app.on_event("shutdown")
def shutdown_event():
    # Close the RabbitMQ connection
    connection.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=5001, log_level="debug")
