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

RUN pip install uwsgi uvicorn celery flask-asgi

COPY nginx.conf /etc/nginx/nginx.conf

RUN echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf

ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL
RUN flask db upgrade

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
