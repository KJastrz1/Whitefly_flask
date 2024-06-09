FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install gunicorn celery

COPY nginx.conf /etc/nginx/nginx.conf

RUN echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf

RUN flask db upgrade

CMD redis-server & \
    celery -A app.celery worker --loglevel=info & \
    gunicorn --workers 4 --bind 0.0.0.0:8000 app:app & \
    nginx -g "daemon off;"
