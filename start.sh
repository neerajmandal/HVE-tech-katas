#!/bin/bash
set -e

python manage.py migrate --noinput

exec gunicorn StingrayHealthPortal.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
