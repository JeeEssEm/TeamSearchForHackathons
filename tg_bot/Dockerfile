FROM python:3.12-slim

# Устанавливаем системные зависимости для компиляции расширений C (например, asyncpg)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./tg_bot /app
COPY ./core /app/core

# Добавляем core в PYTHONPATH
ENV PYTHONPATH=/app/core:$PYTHONPATH

# Запуск бота
CMD ["python", "main.py"]