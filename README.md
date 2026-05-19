# Контрольная работа №5 Суринов Артём ЭФБО-03-24
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

# Задание 3: WebSocket-комнаты для обмена сообщениями

## Описание

WebSocket чат с комнатами и HTTP интерфейсом для просмотра активных пользователей.

## Команды

### Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Запуск тестов

```bash
pytest tests/ -v
```

## WebSocket маршрут

```text
ws://localhost:8000/ws/rooms/{room_id}?username={username}
```

### Параметры

- `room_id` — название комнаты
- `username` — имя пользователя (обязательный)

### Коды закрытия

- `1008` — `username` не передан или состоит только из пробелов

## Формат сообщений

### Отправка сообщения

```json
{
  "type": "message",
  "text": "Текст сообщения"
}
```

### Получение сообщения

```json
{
  "type": "message",
  "room_id": "python",
  "username": "alice",
  "text": "Всем привет"
}
```

### Системное сообщение (подключение/отключение)

```json
{
  "type": "system",
  "text": "alice connected to chat",
  "username": "system"
}
```

### Ошибка (сообщение длиннее 300 символов)

```json
{
  "type": "error",
  "detail": "Message is too long"
}
```

## HTTP маршруты

### `GET /rooms/{room_id}/users`

Возвращает список активных пользователей комнаты.

Ответ:

```json
{
  "room_id": "python",
  "users": ["alice", "bob"]
}
```

### `GET /health`

Проверка состояния приложения.

## Пример использования

### Терминал 1 (Алиса)

```bash
websocat "ws://localhost:8000/ws/rooms/python?username=alice"
```

### Терминал 2 (Боб)

```bash
websocat "ws://localhost:8000/ws/rooms/python?username=bob"
```

### Терминал 3 (просмотр пользователей)

```bash
curl http://localhost:8000/rooms/python/users
```

# Задание 4: Внедрение зависимостей и расширенная маршрутизация

## Команды

### Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Запуск тестов

```bash
pytest tests/ -v
```

## Маршруты

| Метод  | Маршрут                    | Описание                          |
|-------:|----------------------------|-----------------------------------|
| GET    | `/health`                  | Проверка состояния                |
| POST   | `/tasks`                   | Создание задачи                   |
| GET    | `/tasks`                   | Список задач                      |
| GET    | `/tasks/{task_id}`         | Получение задачи                  |
| PATCH  | `/tasks/{task_id}/status`  | Изменение статуса                 |
| DELETE | `/tasks/{task_id}`         | Удаление задачи                   |
| GET    | `/users/me`                | Текущий пользователь              |
| GET    | `/users/{user_id}`         | Пользователь по ID                |
| GET    | `/admin/stats`             | Статистика (admin)                |
| DELETE | `/admin/tasks/{task_id}`   | Удаление любой задачи (admin)     |

## Заголовки

| Заголовок       | Значение          | Обязательный |
|----------------|-------------------|--------------|
| `X-User-Id`     | `int`             | Да           |
| `X-User-Role`   | `user` или `admin`| Нет (по умолчанию `user`) |

## Примеры

### Обычный пользователь

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task","description":"test","status":"todo","priority":3}'

curl http://localhost:8000/users/me -H "X-User-Id: 10"
```

### Администратор

```bash
curl http://localhost:8000/admin/stats \
  -H "X-User-Id: 1" \
  -H "X-User-Role: admin"

curl -X DELETE http://localhost:8000/admin/tasks/1 \
  -H "X-User-Id: 1" \
  -H "X-User-Role: admin"
```

## HTTP статусы

| Статус | Описание            |
|------:|---------------------|
| 200   | Успешно             |
| 201   | Создано             |
| 204   | Удалено             |
| 401   | Нет `X-User-Id`      |
| 403   | Нет прав `admin`     |
| 404   | Не найдено          |
| 422   | Ошибка валидации    |
