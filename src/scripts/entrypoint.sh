#!/bin/bash

set -e

echo "Waiting for database..."

while ! nc -z ${DB_HOST} ${DB_PORT}; do sleep 1; done
echo "Connected to database."

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Apply database migrations"
python manage.py makemigrations

python manage.py makemigrations main

python manage.py migrate --noinput

# Start Gunicorn
uvicorn djbot.asgi:application --reload --host 0.0.0.0 --port 8000  --proxy-headers --forwarded-allow-ips=*
