#!/bin/bash

echo "Waiting for PostgreSQL..."

while ! nc -z db 5432; do
  sleep 0.5
done

echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
