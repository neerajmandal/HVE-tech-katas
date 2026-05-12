#!/bin/bash
set -e

python manage.py migrate --noinput

# Seed dummy data (idempotent — uses get_or_create / existence checks).
python manage.py seed_dummy_data

exec gunicorn StingrayHealthPortal.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
