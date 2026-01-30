# coffeeshop-python-course


Заказ в Кофейне (взятая бизнес-тематика) с использованием FastAPI, PostgreSQL, RabbitMQ, и Prometheus.

## Быстрый запуск через Docker

```bash
docker compose up --build
```


- API: http://localhost:8000
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- RabbitMQ UI: http://localhost:15672 (логин: `guest`/ пароль:`guest`)
- Grafana:  http://localhost:3000 (логин: `admin`/ пароль:`admin`)

Локальный запуск API:

```bash
uvicorn app.main:app --reload
```

## Тесты
Проверяется также покрытие тестами на 90%, как было поставлено в условии задания.
```bash
uv run pytest --cov=app --cov=consumer --cov-report=term-missing
```

## Задание
```
Бизнесовая тематика - любая, но есть набор требований, все из которых должны выполняться.

1. В проекте должен быть сервер
2. В проекте должен быть консюмер (Kafka/RabbitMQ - не важно), который в каком-то сценарии должен получать от сервера запросы (например дернули ручку на сервере, он в свою очередь кинула событие на обработку в брокер, консьюмер его обработал)
3. Сервис должен работать с реальной БД (хранить в памяти данные не покатит) - использовать можно что угодно на свое усмотрение
4. Все должно быть обернуто в Docker (самописные сервисы + база + брокер + мониторинг), то есть всю систему локально можно запустить с помощью одной команды docker compose up
5. С сервера должны собираться метрики
6. Весь код должен быть покрыт тестами (покрытие по всему проекту 90%)
7. Проверка тестов автоматизирована через CI
```
## Проверка выполнения требований задания

1. **В проекте есть сервер (API)**
   - FastAPI-приложение создаётся в `app/main.py`, а `/orders` подключаются
     через `app/api/orders.py`.
   - Ссылки: [`app/main.py`](app/main.py), [`app/api/orders.py`](app/api/orders.py)

2. **Есть консюмер (RabbitMQ), сервер публикует события**
   - Сервер публикует событие `order_created` при создании заказа
     (`app/services/orders.py` → `app/services/queue.py`).
   - Консьюмер читает очередь и обновляет статус заказа
     (`consumer/main.py`).
   - Ссылки: [`app/services/orders.py`](app/services/orders.py),
     [`app/services/queue.py`](app/services/queue.py),
     [`consumer/main.py`](consumer/main.py)

3. **Используется реальная БД (PostgreSQL)**
   - Модель `Order` описана в `app/models/order.py`.
   - SQLAlchemy и подключение: `app/db/session.py`.
   - В `docker-compose.yml` есть сервис `db` и URL подключения для API/consumer.
   - Ссылки: [`app/models/order.py`](app/models/order.py),
     [`app/db/session.py`](app/db/session.py),
     [`docker-compose.yml`](docker-compose.yml)

4. **Всё обёрнуто в Docker (API + consumer + DB + broker + мониторинг)**
   - `docker-compose.yml` поднимает `api`, `consumer`, `db`, `rabbitmq`,
     `prometheus`, `grafana`.
   - Dockerfileы: `docker/Dockerfile.api`, `docker/Dockerfile.consumer`.
   - Ссылки: [`docker-compose.yml`](docker-compose.yml),
     [`docker/Dockerfile.api`](docker/Dockerfile.api),
     [`docker/Dockerfile.consumer`](docker/Dockerfile.consumer)

5. **С сервера собираются метрики**
   - Метрики доступны на `/metrics` через `prometheus_fastapi_instrumentator`
     в `app/main.py`.
   - Ссылки: [`app/main.py`](app/main.py),
     [`docker/prometheus.yml`](docker/prometheus.yml)

6. **Покрытие тестами ≥ 90%**
   - Порог покрытия задан в `pyproject.toml` выставлен и определён через `--cov-fail-under=90`.
   - Ссылки: [`pyproject.toml`](pyproject.toml)

7. **CI запускает тесты и выводит покрытие**
   - GitHub Actions: `.github/workflows/ci.yml`, в логах есть coverage.
   - Ссылки: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## План проверки

1. Docker
```bash
docker compose up --build
```

2. Создать запрос на заказ
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Alex","item":"Latte"}'

curl http://localhost:8000/orders/1
```
```terminaloutput
{"id":1,"customer_name":"Alex","item":"Latte","status":"created","created_at":"2026-01-30T19:56:15.040564Z"}
```

Затем при запросе
```bash
curl http://localhost:8000/orders/1
```
Ожидаемо статус: `status` меняется с `created` на `processed`.
```terminaloutput
{"id":1,"customer_name":"Alex","item":"Latte","status":"processed","created_at":"2026-01-30T19:56:15.040564Z"}
```

3. Проверить хранение записей в БД
```bash
docker compose exec db psql -U postgres -d coffeeshop -c "SELECT id, customer_name, item, status FROM orders;"
```
Будет видна таблица базы данных с новой записью.
```terminaloutput
 id | customer_name | item  |  status   
----+---------------+-------+-----------
  1 | Alex          | Latte | processed
(1 row)
```
4. Можно проверить эндпойнт на метрики
```bash
curl http://localhost:8000/metrics
``` 
Будут показаны Prometheus метрики.
```terminaloutput
http_request_duration_seconds_created{handler="/metrics",method="GET"} 1.769802278193131e+09
http_request_duration_seconds_created{handler="none",method="GET"} 1.7698023043268297e+09
http_request_duration_seconds_created{handler="/docs",method="GET"} 1.7698023138269825e+09
http_request_duration_seconds_created{handler="/openapi.json",method="GET"} 1.7698023152385926e+09
http_request_duration_seconds_created{handler="/orders",method="POST"} 1.769802975094932e+09
http_request_duration_seconds_created{handler="/orders/{order_id}",method="GET"} 1.7698029751473966e+09
```
5. Запустить тесты с проверкой на покрытие
```bash
uv run pytest --cov=app --cov=consumer --cov-report=term-missing
```
Будет показан отчёт по тестам и выполнение ожидаемого требования на покрытие тестами на >=90%
```terminaloutput.................                                                                          [100%]
========================================= tests coverage =========================================
________________________ coverage: platform darwin, python 3.13.5-final-0 ________________________

Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/__init__.py                    0      0   100%
app/api/__init__.py                0      0   100%
app/api/orders.py                 23      1    96%   28
app/core/__init__.py               0      0   100%
app/core/config.py                 8      0   100%
app/db/__init__.py                 0      0   100%
app/db/base.py                     3      0   100%
app/db/deps.py                     8      0   100%
app/db/session.py                  5      0   100%
app/main.py                        9      0   100%
app/models/__init__.py             2      0   100%
app/models/order.py               11      0   100%
app/repositories/__init__.py       0      0   100%
app/repositories/orders.py        25      0   100%
app/schemas/__init__.py            0      0   100%
app/schemas/order.py              12      0   100%
app/services/__init__.py           0      0   100%
app/services/errors.py             4      0   100%
app/services/events.py             3      0   100%
app/services/orders.py            16      0   100%
app/services/queue.py             13      0   100%
consumer/__init__.py               0      0   100%
consumer/main.py                  43      8    81%   74-82, 86
------------------------------------------------------------
TOTAL                            185      9    95%
Required test coverage of 90% reached. Total coverage: 95.14%
17 passed in 0.63s                          
```

## Проверка Grafana

Grafana включена в Docker Compose.

1) Запустить Docker
```bash
docker compose up --build
```

2) Открыть Grafana http://localhost:3000 (логин: `admin`/ пароль:`admin`).

3) Также для примера Prometheus источник данныз и дашборд уже имеются подгруженными, но можно настроить и отдельный Dashboard&
