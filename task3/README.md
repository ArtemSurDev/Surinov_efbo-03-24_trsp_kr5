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