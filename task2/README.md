# Задание 2: Docker-контейнеризация FastAPI-приложения

## Описание

FastAPI-приложение для управления задачами, упакованное в Docker-контейнер.

## Команды

### Создание виртуального окружения и установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Запуск приложения локально

```bash
uvicorn app.main:app --reload
```

### Запуск тестов

```bash
pytest tests/ -v
```

### Сборка и запуск Docker-контейнера

```bash
docker compose up --build
```

### Проверка работы

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

## Маршруты

- `GET /health` — проверка состояния
- `POST /tasks` — создание задачи
- `GET /tasks` — список задач
- `GET /tasks/{task_id}` — получение задачи
- `PATCH /tasks/{task_id}/status` — изменение статуса
- `DELETE /tasks/{task_id}` — удаление задачи

## Переменные окружения

- `APP_ENV=docker` — устанавливается в `docker-compose.yml`

## Инструкция по запуску

```bash
cd task2
docker compose up --build
```

В другом терминале:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

Ожидаемый результат для пустого списка:

```json
[]
```