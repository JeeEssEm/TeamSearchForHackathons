FROM python:3.12-slim

# Устанавливаем системные зависимости для компиляции расширений C
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./admin /app
COPY ./core /app/core

# Устанавливаем PYTHONPATH для доступа к core
ENV PYTHONPATH=/app:$PYTHONPATH

# Запуск приложения
CMD ["uvicorn", "teamsearchadmin.asgi:application", "--host", "0.0.0.0", "--port", "8000"]