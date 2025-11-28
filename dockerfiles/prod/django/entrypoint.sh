#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate


# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput


# Start the server or any other command passed as argument
echo "Starting server..."
gunicorn --bind 0.0.0.0:8000 --workers 17 core.wsgi:application

