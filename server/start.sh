#!/bin/bash
set -e

echo "Iniciando aplicação..."

# Verificar se estamos no Railway
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "Ambiente Railway detectado"
    export PORT=${PORT:-8000}
else
    echo "Ambiente local detectado"
    export PORT=8000
fi

# Verificar variáveis de ambiente críticas
echo "Verificando variáveis de ambiente..."
echo "PORT: ${PORT}"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-email_classifier.settings}"
echo "PWD: $(pwd)"
echo "Arquivos no diretório: $(ls -la)"

# Configurar Django
export DJANGO_SETTINGS_MODULE=email_classifier.settings
export PYTHONPATH=/app:$PYTHONPATH

# Verificar se o Python consegue encontrar o Django
echo "Testando importação do Django..."
python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python path: {sys.path[:5]}')

try:
    import django
    print(f'Django importado: versão {django.get_version()}')
except ImportError as e:
    print(f'Erro ao importar Django: {e}')
    sys.exit(1)
"

# Verificar se o manage.py funciona
echo "Testando manage.py..."
python3 manage.py --version

# Verificar se o Django consegue inicializar
echo "Testando configuração do Django..."
python3 -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_classifier.settings')
try:
    django.setup()
    print('Django configurado com sucesso')
except Exception as e:
    print(f'Erro na configuração do Django: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Esperar o banco de dados ficar disponível (se PostgreSQL)
echo "Verificando banco de dados..."
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

# Verificar se o Django consegue inicializar completamente
echo "Verificando Django com --check..."
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

# Teste rápido da aplicação Django
echo "Testando importação de views..."
python3 -c "
try:
    from classifier.views import api_status
    from django.test import RequestFactory
    request = RequestFactory().get('/api/status/')
    response = api_status(request)
    print(f'View api_status retornou status: {response.status_code}')
except Exception as e:
    print(f'Erro ao testar view: {e}')
    import traceback
    traceback.print_exc()
"

echo "Iniciando servidor Gunicorn..."
echo "DEBUG=${DEBUG:-False}"
echo "PORT=${PORT}"
echo "ALLOWED_HOSTS=${ALLOWED_HOSTS:-all}"

# Configurações importantes para o CORS e CSRF
export CORS_ALLOW_ALL_ORIGINS=True
export CORS_ORIGIN_WHITELIST=${CORS_ORIGIN_WHITELIST:-"https://email-classifier-ten.vercel.app,http://localhost:3000"}

# Iniciar o servidor com configuração otimizada para Railway
exec gunicorn email_classifier.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output
