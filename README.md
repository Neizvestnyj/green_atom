Для локального запуска ставим https://www.erlang.org/downloads
Потом https://www.rabbitmq.com/docs/install-windows#installer
https://redisant.com/rta

Решение ошибки с RabbitMQ
windows https://stackoverflow.com/questions/61768347/rabbit-mq-error-unable-to-perform-an-operation-on-node-rabbitusername

`pip install -r requirements.txt`

Запуск приложений:
`cd organization_service; uvicorn main:app --host localhost --port 5000 --reload --log-level debug`
`cd storage_service; uvicorn main:app --host localhost --port 5001 --reload --log-level debug`

rabbitmqctl list_queues
