FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./tg_bot /app

# Добавляем core в PYTHONPATH
ENV PYTHONPATH=/app/core:$PYTHONPATH

CMD ["python", "main.py"]
