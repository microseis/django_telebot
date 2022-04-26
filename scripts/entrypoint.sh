#!/bin/sh

set -e

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Apply database migrations"
python manage.py makemigrations

python manage.py makemigrations main

python manage.py migrate --noinput

uwsgi --socket :8000 --master  --module djbot.wsgi

echo "Telebot launching"
python manage.py bot
