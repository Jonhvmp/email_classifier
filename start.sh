#!/bin/bash

# Verificar se temos DATABASE_URL (indicativo do Railway)
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não definida. Verifique se o serviço PostgreSQL está conectado no Railway."
    exit 1
fi

echo "✅ DATABASE_URL encontrada"
echo "🔗 Conectando ao banco de dados..."

# Aguardar um momento para conexões se estabilizarem
sleep 2

# Verificar conectividade básica
echo "🧪 Testando conectividade com banco..."
cd server
python manage.py check --database default --deploy || {
    echo "❌ Falha na verificação do banco de dados"
    exit 1
}

echo "✅ Verificação do banco OK"

# Executar migrações
echo "📦 Aplicando migrações..."
python manage.py migrate --noinput || {
    echo "❌ Falha ao aplicar migrações"
    exit 1
}

echo "✅ Migrações aplicadas"

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput || {
    echo "❌ Falha ao coletar arquivos estáticos"
    # Não fazer exit aqui, pois arquivos estáticos não são críticos
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
