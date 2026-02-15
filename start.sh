#!/bin/sh

mkdir -p /app/media /app/static /app/logs

python manage.py collectstatic --noinput

gunicorn liu_genealogy.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log
