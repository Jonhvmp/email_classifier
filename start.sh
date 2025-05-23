#!/bin/bash
cd server

# Aguardar o banco de dados estar pronto
echo "Verificando conexão com banco de dados..."
python wait_for_db.py

# Executar migrações
echo "Aplicando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar servidor
echo "Iniciando servidor Gunicorn..."
gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 2
