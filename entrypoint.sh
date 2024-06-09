#!/bin/sh

redis-server &

celery -A app.celery worker --loglevel=info &

if [ "$SERVER_TYPE" = "asgi" ]; then
    uvicorn app:asgi_app --host 0.0.0.0 --port 8000 &
else
    uwsgi --http :8000 --module app:app &
fi

nginx -g "daemon off;"
