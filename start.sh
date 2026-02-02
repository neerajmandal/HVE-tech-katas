#!/bin/bash

# Local development script for Broader Django app
# Sets DEBUG=TRUE and starts the Django development server

echo "Starting Broader web app for local development..."
echo "Setting DEBUG=TRUE for local development"

echo "Compiling Tailwind CSS..."
npx @tailwindcss/cli -i static/input.css -o static/output.css --config tailwind.config.js

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Waiting for CSS compilation to finish..."
sleep 2

export DEBUG=true
python manage.py runserver