#!/bin/bash

set -e

echo "Waiting for database..."

while ! nc -z ${DB_HOST} ${DB_PORT}; do sleep 1; done
echo "Connected to database."

python manage.py bot
