# admin/Dockerfile
FROM python:3.10-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем зависимостя и устанавливаем их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY ./admin /app

# ENV PYTHONPATH=/app/core:$PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH
# Запуск приложения
CMD ["python", "manage.py"]
