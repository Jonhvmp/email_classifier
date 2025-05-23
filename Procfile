web: cd server && python manage.py migrate && python manage.py collectstatic --noinput && python -m gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT --workers 2
