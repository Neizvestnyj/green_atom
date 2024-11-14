[![Codecov](https://codecov.io/gh/Neizvestnyj/green_atom/branch/master/graph/badge.svg)](https://codecov.io/gh/Neizvestnyj/green_atom)

Для локального запуска ставим https://www.erlang.org/downloads
Потом https://www.rabbitmq.com/docs/install-windows#installer
https://redisant.com/rta

Решение ошибки с RabbitMQ
windows https://stackoverflow.com/questions/61768347/rabbit-mq-error-unable-to-perform-an-operation-on-node-rabbitusername

`pip install -r requirements.txt`

Запуск приложений:
`cd organization_service; uvicorn main:app --host localhost --port 8000 --reload --log-level debug`
`cd storage_service; uvicorn main:app --host localhost --port 8001 --reload --log-level debug`

Смотрим, что появилась запись в очереди `rabbitmqctl list_queues`
Список подписок: `rabbitmqctl list_bindings`

# Деплой

```shell
docker-compose up --build
```

# Запуск тестов

```shell
pytest organization_service/tests
pytest storage_service/tests
```

## Тесты с данными о покрытии
```shell
coverage run -m pytest organization_service/tests
coverage run -m pytest storage_service/tests
coverage report -m
coverage html
```
