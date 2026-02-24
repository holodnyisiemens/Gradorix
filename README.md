# Gradorix

Gradorix - система для помощи в развитии и мониторинга успехов молодых специалистов.

## Запуск проекта локально

На хосте должны быть установлены:
1. СУБД PostgreSQL 15 или выше, а также создана в нем БД `gradorix`
2. Python 3.12 или выше

Запустить проект можно через выполнение нижеуказанных команд. Для этого можно использовать терминал, например, cmd или PowerShell (для Windows), sh или bash (для Linux) и другие.

1. Клонируем проект и переходим в рабочую директорию проекта:

Если установлен Git (иначе скачиваем через GitHub, перейдя по ссылке):
```
git clone https://github.com/holodnyisiemens/Gradorix.git
```
```
cd Gradorix
```

2. Создаем виртуальное окружение:

Для Windows:
```
python -m venv .venv
```

Для Linux:
```
python3 -m venv .venv
```

3. Активируем виртуальное окружение:

Для Windows:
```
.\.venv\Scripts\activate
```

Для Linux:
```
source ./.venv/bin/activate
```

4. Устанавливаем зависимости:

Установка менеджера пакетов Poetry:
```
pip install poetry
```

Установка зависимостей проекта через Poetry:
```
poetry install
```

5. На основе шаблона настроек .env.template создаем файл .env.local и настраиваем его:

`DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME` - настройки подключения к БД PostgreSQL

6. Применяем миграции для БД:
```
alembic upgrade head
```

7. Запускаем проект:
```
python -m app.main
```

Остановить проект можно через сочетание клавиш Ctrl+C.
Деактивировать виртуальное окружение можно через команду `deactivate`.
