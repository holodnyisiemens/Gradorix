FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    pkg-config \
    libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
