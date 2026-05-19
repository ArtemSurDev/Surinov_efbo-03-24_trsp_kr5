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