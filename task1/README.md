# Задание 1: Интеграционные тесты для API задач

## Описание

FastAPI-приложение для управления задачами с интеграционными тестами.

## Функциональность

- Создание задачи (`POST /tasks`)
- Получение списка задач текущего пользователя (`GET /tasks`)
- Получение одной задачи (`GET /tasks/{task_id}`)
- Изменение статуса задачи (`PATCH /tasks/{task_id}/status`)
- Удаление задачи (`DELETE /tasks/{task_id}`)
- Проверка состояния приложения (`GET /health`)

## Аутентификация

Используется заголовок `X-User-Id` для идентификации пользователя.

## Установка и запуск

### 1) Создание виртуального окружения

```bash
python -m venv .venv
```

### 2) Активация виртуального окружения

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3) Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4) Запуск приложения

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`

## Документация API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Запуск тестов

```bash
pytest tests/ -v
```

Для просмотра покрытия (coverage):

```bash
pytest tests/ -v --cov=app
```

## Примеры запросов

### Создание задачи

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Подготовить тесты",
    "description": "Написать интеграционные тесты",
    "status": "todo",
    "priority": 4
  }'
```

### Получение списка задач

```bash
curl http://localhost:8000/tasks/ -H "X-User-Id: 10"
```

### Получение задачи по ID

```bash
curl http://localhost:8000/tasks/1 -H "X-User-Id: 10"
```

### Изменение статуса задачи

```bash
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Удаление задачи

```bash
curl -X DELETE http://localhost:8000/tasks/1 -H "X-User-Id: 10"
```

## HTTP статусы

- `200` — успешный `GET` / `PATCH` запрос
- `201` — успешное создание ресурса
- `204` — успешное удаление
- `400` — неверный запрос
- `401` — отсутствует или некорректен `X-User-Id`
- `404` — ресурс не найден
- `422` — ошибка валидации данных