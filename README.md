# Green Atom [![codecov](https://codecov.io/gh/Neizvestnyj/green_atom/branch/master/graph/badge.svg?token=RZJYZXF5WD)](https://codecov.io/gh/Neizvestnyj/green_atom)

## Схемы
### Схема БД
![Схема БД](diagrams/db.png)

### Схема архитектуры
![Схема EDA](diagrams/EDA.png)

### Представление связи организаций и хранилищ
![Связи организаций и хранилищ](diagrams/relationship.png)

## Деплой

```shell
docker-compose build
docker-compose up -d
```

## Скрипт для создания тестовых данных

```shell
python scripts/create_test_data.py
```

## **API для управления организациями и хранилищами**

Все запросы можно запустить с
помощью [Postman](https://www.postman.com/downloads/) [GreenAtom.postman_collection.json](GreenAtom.postman_collection.json)

### **Запросы для микросервиса organisation**

Тело URL: **/api/v1/organisation/**

#### 1. Проверка статуса сервиса

**GET** `/api/v1/organisation/health/`

- Возвращает статус сервиса.

**Пример ответа:**

```json
{
  "status": "OK"
}
```

#### 2. Создание организации

**POST** `/api/v1/organisation/organisation/`

- Создает новую организацию.

**Параметры:**

- `name` (str): Название организации.
- `capacity` (dict): Объем отходов в хранилище. **{"Тип отходов": [сколько отходов уже выработала ОО, максимальная вместим ОО]}**.

**Пример запроса:**

```json
{
 "name": "ОО1",
    "capacity": {
        "Стекло": [100, 100],
        "Биоотходы": [150, 150],
        "Пластик": [20, 20]
    }
}
```

**Пример ответа:**

```json
{
    "name": "ОО1",
    "capacity": {
        "Стекло": [100, 100],
        "Биоотходы": [150, 150],
        "Пластик": [20, 20]
    },
    "id": 1
}
```

#### 3. Получение списка организаций

**GET** `/api/v1/organisation/organisations/`

- Возвращает список всех организаций.

**Пример ответа:**

```json
[
  {
    "name": "ОО1",
    "capacity": {
      "Пластик": [10, 10],
      "Стекло": [50, 50],
      "Биоотходы": [50, 50]
    },
    "id": 1
  },
  {
    "name": "ОО2",
    "capacity": {
      "Пластик": [60, 60],
      "Стекло": [20, 20],
      "Биоотходы": [50, 50]
    },
    "id": 2
  }
]
```

#### 4. Удаление организации

**DELETE** `/api/v1/organisation/organisation/{ID}/`

- Удаляет все организации из базы данных.

**Пример ответа:**

```json
{
  "message": "Организация успешно удалена"
}
```

#### 5. Запрос на переработку отходов

**POST** `/api/v1/organisation/recycle/`

- Распределяет отходы организации по хранилищам.

**Параметры:**

- `organisation_id` (int): ID организации.

**Пример запроса:**

```json
{
  "organisation_id": 1
}
```

**Пример ответа:**

```json
{
  "waste_distribution": {
    "2": {
      "Пластик": 10,
      "Биоотходы": 50
    },
    "1": {
      "Стекло": 50
    }
  },
  "message": "Отходы были распределены по хранилищам"
}
```

---

### **Запросы для микросервиса storage**

Тело URL: **/api/v1/storage/**

#### 1. Проверка статуса сервиса

**GET** `/api/v1/storage/health/`

- Возвращает статус сервиса.

**Пример ответа:**

```json
{
  "status": "OK"
}
```

#### 2. Создание хранилища

**POST** `/api/v1/storage/storage/`

- Создает новое хранилище.

**Параметры:**

- `name` (str): Название хранилища.
- `location` (str): Расположение хранилища.
- `capacity` (dict): Вместимость хранилища **{"Тип отходов": [сколько отходов может вместить МНО, максимальная вместим МНО]}**.

**Пример Запроса:**

```json
{
    "name": "МНО1",
    "location": "Москва",
    "capacity": {
        "биоотходы": [0, 300],
        "стекло": [0, 100],
        "пластик": [0, 150]
    }
}
```

**Пример ответа:**

```json
{
    "name": "МНО1",
    "location": "Москва",
    "capacity": {
        "биоотходы": [0, 300],
        "стекло": [0, 100],
        "пластик": [0, 150]
    },
    "id": 9
}
```

#### 3. Создание записи о расстоянии

**POST** `/api/v1/storage/distance/`

- Добавляет расстояние между хранилищем и организацией.

**Параметры:**

- `storage_id` (int): ID хранилища.
- `organisation_id` (int): ID организации.
- `distance` (int): Расстояние в километрах.

**Пример запроса:**

```json
{
  "storage_id": 8,
  "organisation_id": 1,
  "distance": 50
}
```

**Пример ответа:**

```json
{
  "storage_id": 1,
  "organisation_id": 1,
  "distance": 50,
  "id": 12
}
```

#### 4. Получение списка хранилищ

**GET** `/api/v1/storage/storages/`

- Возвращает список всех хранилищ.

**Пример ответа:**

```json
[
    {
        "name": "МНО1",
        "location": "Москва",
        "capacity": {
            "Стекло": [50, 300],
            "Пластик": [0, 100]
        },
        "id": 1
    }
]
```

#### 5. Получение списка расстояний

**GET** `/api/v1/storage/distances/`

- Возвращает список всех расстояний между хранилищами и организациями.

**Пример ответа:**

```json
[
  {
    "storage_id": 1,
    "organisation_id": 1,
    "distance": 100,
    "id": 1
  },
  {
    "storage_id": 2,
    "organisation_id": 1,
    "distance": 50,
    "id": 2
  }
]
```

#### 6. Удаление хранилища

Удаляет каскадно, вместе со `StorageDistance`
**DELETE** `/api/v1/storage/storage/{ID}`

**Пример ответа:**

```json
{
  "message": "Хранилище успешно удалено"
}
```

#### 6. Удаление расстояния

**DELETE** `/api/v1/storage/distance/{ID}`

**Пример ответа:**

```json
{
  "message": "Расстояние между ОО и МНО успешно удалено"
}
```

## Запуск Unit-тестов

> Note: Unit-тесты уже запускаются в процессе выполнения GitHub Workflow

```shell
docker exec -it organisation_service pytest tests
docker exec -it storage_service pytest tests
```
