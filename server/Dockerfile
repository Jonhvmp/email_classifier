FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar e tornar executável o script de inicialização
COPY start.sh .
RUN chmod +x start.sh

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Alterar ownership dos arquivos para o usuário app
RUN chown -R app:app /app

USER app

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/status/ || exit 1

# Comando para iniciar a aplicação
CMD ["./start.sh"]
