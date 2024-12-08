# core/Dockerfile
FROM python:3.10-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем зависимостя и устанавливаем их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY ./core /app

# Здесь нет команды для запуска, потому что это только настройка окружения
CMD ["echo", "Core environment setup complete"]
