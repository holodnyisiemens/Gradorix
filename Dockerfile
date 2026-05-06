FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .

# Удалить дублирующую копию и исправить путь
# COPY entrypoint.sh /entrypoint.sh  # <-- Удалить эту строку

# Сделать файл исполняемым и конвертировать окончания строк
RUN chmod +x /app/entrypoint.sh && sed -i 's/\r$//' /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]