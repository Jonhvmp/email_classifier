#!/bin/bash
set -e

echo "Iniciando aplicação..."

# Verificar variáveis de ambiente críticas
echo "Verificando variáveis de ambiente..."
if [ -z "$DATABASE_URL" ] && [ -z "$PGHOST" ]; then
    echo "DATABASE_URL ou PGHOST não definidos. Usando SQLite."
fi

# Esperar o banco de dados ficar disponível
echo "Aguardando banco de dados..."
python3 -c "
import os
import time
import sys

# Aguardar apenas se estiver usando PostgreSQL
if 'DATABASE_URL' in os.environ or 'PGHOST' in os.environ:
    try:
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
                    print('Banco de dados PostgreSQL conectado!')
                    break
                elif all(k in os.environ for k in ['PGHOST', 'PGDATABASE', 'PGUSER', 'POSTGRES_PASSWORD']):
                    conn = psycopg2.connect(
                        host=os.environ['PGHOST'],
                        port=os.environ.get('PGPORT', '5432'),
                        user=os.environ['PGUSER'],
                        password=os.environ['POSTGRES_PASSWORD'],
                        dbname=os.environ['PGDATABASE']
                    )
                    conn.close()
                    print('Banco de dados PostgreSQL conectado via variáveis PGHOST!')
                    break
            except OperationalError as e:
                attempt += 1
                print(f'Tentativa {attempt}/{max_attempts} - Aguardando banco... ({str(e)})')
                time.sleep(2)
        else:
            print('Não foi possível conectar ao banco de dados PostgreSQL')
            print('Continuando com SQLite como fallback...')
    except ImportError:
        print('Módulo psycopg2 não encontrado, pulando verificação PostgreSQL')
else:
    print('Usando SQLite como banco de dados')
" || {
    echo "Erro na verificação de banco de dados"
    echo "Continuando mesmo assim..."
}

# Preparar diretórios
echo "Criando diretórios necessários..."
mkdir -p media/uploads
mkdir -p static
mkdir -p staticfiles

# Executar migrações
echo "Executando migrações..."
python3 manage.py migrate --noinput || {
    echo "Erro nas migrações, tentando novamente após um delay..."
    sleep 5
    python3 manage.py migrate --noinput
}

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

# Verificar se o Django consegue inicializar
echo "Verificando Django..."
python3 manage.py check

# Criar superusuário se não existir
echo "Verificando superusuário..."
python3 manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

echo "Iniciando servidor Gunicorn..."
echo "DEBUG=${DEBUG:-False}"
echo "ALLOWED_HOSTS=${ALLOWED_HOSTS:-all}"
echo "CORS_ALLOW_ALL_ORIGINS=True"

# Configurações importantes para o CORS e CSRF
export DJANGO_SETTINGS_MODULE=email_classifier.settings
export CORS_ALLOW_ALL_ORIGINS=True
export CORS_ORIGIN_WHITELIST=${CORS_ORIGIN_WHITELIST:-"https://email-classifier-ten.vercel.app,http://localhost:3000"}

# Iniciar o servidor com configuração robusta
exec gunicorn email_classifier.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
