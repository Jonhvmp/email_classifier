FROM python:3.13-slim

WORKDIR /app

# Instalar dependências e pacotes necessários
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código-fonte
COPY . .

# Expor a porta que o Django vai usar
EXPOSE 8001

# Comando para iniciar o servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
