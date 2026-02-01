FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости (минимум)
RUN apt-get update && apt-get install -y \
    curl \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Зависимости (кешируем)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Код
COPY . .

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
