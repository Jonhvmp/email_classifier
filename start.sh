#!/bin/bash
cd server
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT --workers 2
