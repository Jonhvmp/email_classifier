web: cd server && python manage.py migrate && gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT
