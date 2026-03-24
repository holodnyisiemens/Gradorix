# Gradorix — Backend API

Система управления программой менторства для молодых специалистов.
Роли: **HR**, **MENTOR**, **JUNIOR**.

---

## Стек

- **FastAPI** + **Uvicorn** (async, hot-reload)
- **SQLAlchemy 2.0** async (asyncpg)
- **PostgreSQL 15+**
- **Alembic** — миграции
- **Pydantic v2** — валидация
- **Poetry** — зависимости

---

## Быстрый старт — Docker (рекомендуется)

Требования: [Docker](https://docs.docker.com/get-docker/) + Docker Compose.

```bash
git clone https://github.com/holodnyisiemens/Gradorix.git
cd Gradorix
docker compose up --build
```

Контейнер сам:
1. Ждёт готовности PostgreSQL
2. Применяет все миграции (`alembic upgrade head`)
3. Запускает сервер на `http://0.0.0.0:8000`

**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
**ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Остановить:
```bash
docker compose down
```

Остановить и удалить данные БД:
```bash
docker compose down -v
```

---

## Локальный запуск (без Docker)

**Требования:** Python 3.12+, PostgreSQL 15+, Poetry.

### 1. Клонировать репозиторий

```bash
git clone https://github.com/holodnyisiemens/Gradorix.git
cd Gradorix
```

### 2. Установить зависимости

```bash
pip install poetry
poetry install
```

### 3. Настроить окружение

Скопировать шаблон и заполнить:

```bash
cp .env.template .env.local
```

`.env.local`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=gradorix

SECRET_KEY=your-secret-key
HASH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 4. Применить миграции

```bash
alembic upgrade head
```

### 5. Запустить сервер

```bash
python -m app.main
```

Сервер поднимается на `http://localhost:8000`.

---

## Миграции

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Сгенерировать новую миграцию после изменения моделей
alembic revision --autogenerate -m "описание изменений"

# Посмотреть текущее состояние
alembic current
```

---

## API — Справочник эндпоинтов

Базовый URL: `http://localhost:8000`

### Пользователи `/users`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/users/` | Список всех пользователей |
| `GET` | `/users/{user_id}` | Пользователь по ID |
| `POST` | `/users/` | Создать пользователя |
| `PATCH` | `/users/{user_id}` | Обновить пользователя |
| `DELETE` | `/users/{user_id}` | Удалить пользователя |

Роли: `HR`, `MENTOR`, `JUNIOR`

---

### Челленджи `/challenges`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/challenges/` | Список всех челленджей |
| `GET` | `/challenges/{challenge_id}` | Челлендж по ID |
| `POST` | `/challenges/` | Создать челлендж |
| `PATCH` | `/challenges/{challenge_id}` | Обновить челлендж |
| `DELETE` | `/challenges/{challenge_id}` | Удалить челлендж |

Статусы: `DRAFT` → `UPCOMING` → `ACTIVE` → `COMPLETED` / `CANCELLED`
Поле `date` (необязательное) — дата дедлайна для отображения в календаре.

---

### Назначения ментор-джуниор `/mentor-junior`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/mentor-junior/` | Список пар. Query: `mentor_id`, `junior_id` |
| `GET` | `/mentor-junior/{mentor_id}/{junior_id}` | Пара по ключу |
| `POST` | `/mentor-junior/` | Назначить ментора джуниору |
| `PATCH` | `/mentor-junior/{mentor_id}/{junior_id}` | Обновить |
| `DELETE` | `/mentor-junior/{mentor_id}/{junior_id}` | Удалить назначение |

---

### Назначения челлендж-джуниор `/challenge-junior`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/challenge-junior/` | Список. Query: `junior_id`, `assigned_by` |
| `GET` | `/challenge-junior/{challenge_id}/{junior_id}` | По ключу |
| `POST` | `/challenge-junior/` | Назначить челлендж джуниору |
| `PATCH` | `/challenge-junior/{challenge_id}/{junior_id}` | Обновить прогресс |
| `DELETE` | `/challenge-junior/{challenge_id}/{junior_id}` | Удалить |

Прогресс: `GOING` → `IN_PROGRESS` → `DONE` / `SKIPPED`

---

### Уведомления `/notifications`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/notifications/` | Список. Query: `user_id` |
| `GET` | `/notifications/{notification_id}` | По ID |
| `POST` | `/notifications/` | Создать уведомление |
| `PATCH` | `/notifications/{notification_id}` | Обновить (например, `is_read`) |
| `DELETE` | `/notifications/{notification_id}` | Удалить |

Поле `created_at` выставляется автоматически.

---

### События календаря `/calendar-events`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/calendar-events/` | Список. Query: `date`, `event_type` |
| `GET` | `/calendar-events/{event_id}` | По ID |
| `POST` | `/calendar-events/` | Создать событие |
| `PATCH` | `/calendar-events/{event_id}` | Обновить |
| `DELETE` | `/calendar-events/{event_id}` | Удалить |

Типы (`event_type`): `challenge`, `meeting`, `deadline`
Поле `challenge_id` — опциональная ссылка на челлендж.

---

### Достижения `/achievements`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/achievements/` | Список всех достижений |
| `GET` | `/achievements/{achievement_id}` | По ID |
| `POST` | `/achievements/` | Создать достижение |
| `PATCH` | `/achievements/{achievement_id}` | Обновить |
| `DELETE` | `/achievements/{achievement_id}` | Удалить |

Категории: `milestone`, `challenge`, `streak`, `social`, `special`

---

### Достижения пользователей `/user-achievements`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/user-achievements/` | Список. Query: `user_id` |
| `GET` | `/user-achievements/{user_id}/{achievement_id}` | По ключу |
| `POST` | `/user-achievements/` | Выдать достижение пользователю |
| `PATCH` | `/user-achievements/{user_id}/{achievement_id}` | Обновить дату получения |
| `DELETE` | `/user-achievements/{user_id}/{achievement_id}` | Забрать достижение |

---

### Баллы и уровни `/user-points`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/user-points/leaderboard` | Лидерборд (по убыванию баллов, с рангом) |
| `GET` | `/user-points/{user_id}` | Баллы конкретного пользователя |
| `POST` | `/user-points/` | Создать запись о баллах |
| `PATCH` | `/user-points/{user_id}` | Обновить баллы/уровень |
| `DELETE` | `/user-points/{user_id}` | Удалить запись |

Поле `rank` в ответе вычисляется динамически.

---

### Активности `/activities`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/activities/` | Список. Query: `user_id`, `activity_status` |
| `GET` | `/activities/{activity_id}` | По ID |
| `POST` | `/activities/` | Создать заявку на баллы |
| `PATCH` | `/activities/{activity_id}` | Обновить (HR подтверждает/отклоняет) |
| `DELETE` | `/activities/{activity_id}` | Удалить |

Статусы: `pending`, `approved`, `rejected`, `revision`
Типы (`activity_type`): `achievement`, `task`, `test`, `event`, `custom`

---

### Команды `/teams`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/teams/` | Список. Query: `mentor_id` |
| `GET` | `/teams/{team_id}` | По ID (включает `member_ids`) |
| `POST` | `/teams/` | Создать команду |
| `PATCH` | `/teams/{team_id}` | Обновить (в т.ч. состав `member_ids`) |
| `DELETE` | `/teams/{team_id}` | Удалить |

Поле `member_ids` — список ID пользователей-участников. При PATCH полностью заменяет состав.
Статусы: `active`, `on_hold`, `completed`

---

### Квизы `/quizzes`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/quizzes/` | Список. Query: `available` (bool) |
| `GET` | `/quizzes/{quiz_id}` | По ID (включает вопросы) |
| `POST` | `/quizzes/` | Создать квиз |
| `PATCH` | `/quizzes/{quiz_id}` | Обновить |
| `DELETE` | `/quizzes/{quiz_id}` | Удалить |

Поле `questions` — JSON-массив объектов `{id, text, type, options?, correctAnswers?}`.
Типы вопросов: `single`, `multiple`, `text`.

---

### Результаты квизов `/quiz-results`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/quiz-results/` | Список. Query: `user_id`, `quiz_id` |
| `GET` | `/quiz-results/{result_id}` | По ID |
| `POST` | `/quiz-results/` | Сохранить результат |
| `DELETE` | `/quiz-results/{result_id}` | Удалить |

Поле `score` — процент правильных ответов (0–100).

---

### База знаний `/kb-sections`, `/kb-articles`

**Разделы:**

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/kb-sections/` | Список разделов (по `order`) |
| `GET` | `/kb-sections/{section_id}` | Раздел по ID |
| `POST` | `/kb-sections/` | Создать раздел |
| `PATCH` | `/kb-sections/{section_id}` | Обновить |
| `DELETE` | `/kb-sections/{section_id}` | Удалить (каскадно удаляет статьи) |

**Статьи:**

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/kb-articles/` | Список. Query: `section_id` |
| `GET` | `/kb-articles/{article_id}` | Статья по ID |
| `POST` | `/kb-articles/` | Создать статью |
| `PATCH` | `/kb-articles/{article_id}` | Обновить |
| `DELETE` | `/kb-articles/{article_id}` | Удалить |

---

### Посещаемость встреч `/meeting-attendance`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/meeting-attendance/` | Список. Query: `event_id`, `user_id` |
| `GET` | `/meeting-attendance/{attendance_id}` | По ID |
| `POST` | `/meeting-attendance/` | Отметить посещение |
| `PATCH` | `/meeting-attendance/{attendance_id}` | Обновить отметку |
| `DELETE` | `/meeting-attendance/{attendance_id}` | Удалить |

---

## Архитектура

```
app/
├── main.py              # FastAPI app + подключение роутеров
├── dependencies.py      # DI-зависимости (сервисы через Depends)
├── core/
│   ├── config.py        # Настройки (pydantic-settings, читает .env.local)
│   ├── database.py      # Async + sync движки SQLAlchemy
│   └── enums.py         # Все перечисления (роли, статусы, типы)
├── models/              # SQLAlchemy ORM-модели
├── schemas/             # Pydantic DTOs (CreateDTO / ReadDTO / UpdateDTO)
├── repositories/        # Слой доступа к данным (AsyncSession)
├── services/            # Бизнес-логика, HTTP-исключения
├── routers/             # FastAPI-роутеры
└── auth/                # JWT-утилиты, bcrypt
```

**Слои запроса:** Router → Service → Repository → Database

**Паттерны:**
- Repository pattern — весь доступ к БД изолирован в репозиториях
- DTO split — `CreateDTO` / `ReadDTO` / `UpdateDTO` для каждой сущности
- Async-first — все запросы к БД через `AsyncSession`

---

## Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `DB_HOST` | Хост PostgreSQL | `localhost` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `postgres` |
| `DB_NAME` | Имя БД | `gradorix` |
| `SECRET_KEY` | Ключ для JWT | `your-secret-key` |
| `HASH_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access токена | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh токена | `7` |
