#!/bin/bash

# Verificar variáveis do Railway PostgreSQL
echo "🔍 Verificando configurações do Railway PostgreSQL..."

if [ -n "$PGHOST" ] && [ -n "$PGDATABASE" ] && [ -n "$PGUSER" ] && [ -n "$POSTGRES_PASSWORD" ]; then
    echo "✅ Variáveis PostgreSQL encontradas:"
    echo "   PGHOST: $PGHOST"
    echo "   PGDATABASE: $PGDATABASE"
    echo "   PGUSER: $PGUSER"
    echo "   PGPORT: ${PGPORT:-5432}"
elif [ -n "$DATABASE_URL" ]; then
    echo "✅ DATABASE_URL encontrada: ${DATABASE_URL:0:50}..."
else
    echo "❌ Configurações de banco de dados não encontradas!"
    echo "Variáveis disponíveis:"
    env | grep -E "(DATABASE|PG|POSTGRES)" | sort
    exit 1
fi

echo "🔗 Conectando ao banco de dados PostgreSQL..."

# Aguardar um momento para conexões se estabilizarem
sleep 3

# Entrar no diretório server
cd server

# Verificar se os arquivos do Django existem
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py não encontrado no diretório server"
    exit 1
fi

# Mostrar informações de debug do Django
echo "🧪 Verificando configurações do Django..."
python manage.py diffsettings | grep -i database || echo "Não foi possível mostrar configurações"

# Verificar conectividade básica
echo "🧪 Testando conectividade básica com banco..."
python manage.py check --database default || {
    echo "❌ Falha na verificação básica do Django"
    echo "Tentando diagnosticar o problema..."
    python manage.py shell -c "
import os
print('DATABASE_URL:', os.environ.get('DATABASE_URL', 'NÃO DEFINIDA'))
print('PGHOST:', os.environ.get('PGHOST', 'NÃO DEFINIDA'))
print('PGDATABASE:', os.environ.get('PGDATABASE', 'NÃO DEFINIDA'))
from django.conf import settings
print('Engine configurado:', settings.DATABASES['default']['ENGINE'])
print('Host configurado:', settings.DATABASES['default'].get('HOST', 'N/A'))
"
    exit 1
}

echo "✅ Verificação básica OK"

# Executar migrações com mais verbosidade
echo "📦 Aplicando migrações..."
python manage.py migrate --verbosity=2 --noinput || {
    echo "❌ Falha ao aplicar migrações"
    exit 1
}

echo "✅ Migrações aplicadas"

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput || {
    echo "⚠️ Falha ao coletar arquivos estáticos, mas continuando..."
}

echo "✅ Arquivos estáticos coletados"

# Verificar se gunicorn está disponível
echo "🔍 Verificando se gunicorn está disponível..."
python -c "import gunicorn; print('✅ Gunicorn encontrado')" || {
    echo "❌ Gunicorn não encontrado"
    exit 1
}

# Iniciar servidor
echo "🚀 Iniciando servidor Gunicorn..."
echo "🌐 Servidor será iniciado na porta: ${PORT:-8000}"

gunicorn email_classifier.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --keep-alive 2 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
