#!/bin/bash
set -e

echo "Iniciando aplicação..."

# Esperar o banco de dados ficar disponível
echo "Aguardando banco de dados..."
python -c "
import os
import time
import psycopg2
from psycopg2 import OperationalError

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        if 'DATABASE_URL' in os.environ:
            import dj_database_url
            db_config = dj_database_url.parse(os.environ['DATABASE_URL'])
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                dbname=db_config['NAME']
            )
            conn.close()
            print('Banco de dados conectado!')
            break
        else:
            print('Usando SQLite local')
            break
    except OperationalError:
        attempt += 1
        print(f'Tentativa {attempt}/{max_attempts} - Aguardando banco...')
        time.sleep(2)
else:
    print('Não foi possível conectar ao banco de dados')
    exit(1)
"

# Executar migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Criar superusuário se não existir
echo "Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

echo "Iniciando servidor..."
exec gunicorn email_classifier.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info
