# Guia de Deployment

## Preparação para Produção

### 1. Configurações de Segurança

#### settings.py
```python
# Nunca True em produção
DEBUG = False

# Hosts específicos para Railway
ALLOWED_HOSTS = ['*.railway.app', 'domainname.com']

# Chave secreta forte
SECRET_KEY = os.getenv('SECRET_KEY')  # Do .env

# HTTPS apenas (Railway fornece SSL automático)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### Variáveis de Ambiente para Railway
```bash
SECRET_KEY=sua-chave-super-secreta-de-producao
DEBUG=False
ALLOWED_HOSTS=*.railway.app,domainname.com
GEMINI_API_KEY=sua-chave-de-producao
CORS_ORIGIN_FRONT=https://seu-app.railway.app
```

### 2. Configuração do Banco de Dados

#### PostgreSQL na Railway
A Railway fornece PostgreSQL como add-on. As variáveis são injetadas automaticamente:

```python
# settings.py - Configuração para Railway
import dj_database_url

# Railway injeta DATABASE_URL automaticamente
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}
```

#### Dependências adicionais
```bash
# Adicionar ao requirements.txt
dj-database-url>=1.0.0
psycopg2-binary>=2.9.0
```

### 3. Arquivos Estáticos

#### Configuração para Railway
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware do WhiteNoise (já configurado)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Logo após SecurityMiddleware
    # ... outros middlewares
]
```

## Deployment na Railway

### 1. Preparação do Projeto

#### Criar requirements.txt atualizado
```txt
# filepath: c:\Users\plugify\Documents\GitHub\email_classifier\server\requirements.txt
# ...existing code...
dj-database-url>=1.0.0
psycopg2-binary>=2.9.0
```

#### Procfile para Railway
```procfile
# filepath: c:\Users\plugify\Documents\GitHub\email_classifier\Procfile
web: cd server && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT
```

#### railway.json (Opcional)
```json
# filepath: c:\Users\plugify\Documents\GitHub\email_classifier\railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd server && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/status/"
  }
}
```

### 2. Deploy via GitHub

#### Passo a Passo
1. **Conectar Repository**:
   ```bash
   # Fazer push do código para GitHub
   git add .
   git commit -m "Preparar para deploy na Railway"
   git push origin main
   ```

2. **Acessar Railway Console**:
   - Vá para [railway.app](https://railway.app)
   - Faça login com GitHub
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"

3. **Configurar Projeto**:
   - Selecione o repositório `email_classifier`
   - Railway detectará automaticamente que é um projeto Python

4. **Adicionar PostgreSQL**:
   - No dashboard do projeto, clique em "New"
   - Selecione "Database" → "PostgreSQL"
   - Railway criará automaticamente a variável `DATABASE_URL`

### 3. Configurar Variáveis de Ambiente

No dashboard da Railway, vá em "Variables" e adicione:

```bash
# Obrigatórias
SECRET_KEY=sua-chave-secreta-django
GEMINI_API_KEY=sua-chave-api-gemini
DEBUG=False

# Opcional (Railway configura automaticamente)
ALLOWED_HOSTS=*.railway.app
PORT=8000
```

### 4. Configurações Avançadas

#### Custom Domain (Opcional)
```bash
# No dashboard Railway:
# Settings → Domains → Add Custom Domain
# Adicionar: domainname.com
```

#### Health Check
```python
# O endpoint /api/status/ já serve como health check
# Railway verificará automaticamente este endpoint
```

## Deployment via CLI da Railway

### 1. Instalação da CLI

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Ou via Homebrew (Mac)
brew install railway

# Login
railway login
```

### 2. Deploy via CLI

```bash
# No diretório do projeto
cd email_classifier

# Inicializar projeto Railway
railway init

# Fazer deploy
railway up

# Adicionar PostgreSQL
railway add --database postgresql

# Ver logs
railway logs

# Abrir no browser
railway open
```

### 3. Comandos Úteis

```bash
# Ver status do deploy
railway status

# Executar comandos no servidor
railway run python server/manage.py shell

# Ver variáveis de ambiente
railway variables

# Conectar ao banco de dados
railway connect postgresql
```

## Configurações de Produção

### 1. settings.py para Railway

```python
# filepath: c:\Users\plugify\Documents\GitHub\email_classifier\server\email_classifier\settings.py
# ...existing code...

import dj_database_url

# Database configuration for Railway
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback para desenvolvimento local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Configurações de segurança para produção
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CORS configuration para Railway
CORS_ALLOWED_ORIGINS = [
    os.getenv('CORS_ORIGIN_FRONT', 'http://localhost:3000'),
]

if not DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        'https://seu-app.railway.app',
        'https://domainname.com',
    ])
```

### 2. Logging para Railway

```python
# Adicionar ao settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'classifier': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Monitoramento e Manutenção

### 1. Logs da Railway

```bash
# Ver logs em tempo real
railway logs --follow

# Logs de deploy
railway logs --deployment

# Filtrar logs por serviço
railway logs --service web
```

### 2. Health Checks

A Railway monitora automaticamente o endpoint:
```
https://seu-app.railway.app/api/status/
```

### 3. Backup do Banco de Dados

```bash
# Fazer backup via Railway CLI
railway connect postgresql
# No console do PostgreSQL:
pg_dump -h hostname -U username database_name > backup.sql

# Ou via comando direto
railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### 4. Scaling (Upgrade de Plano)

```bash
# Ver uso atual de recursos
railway metrics

# Configurar autoscaling (planos pagos)
# No dashboard: Settings → Autoscaling
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Build
```bash
# Ver logs detalhados de build
railway logs --deployment

# Rebuild forçado
railway redeploy
```

#### 2. Erro de Database
```bash
# Verificar conexão com banco
railway run python server/manage.py dbshell

# Executar migrations manualmente
railway run python server/manage.py migrate

# Reset do banco (CUIDADO!)
railway run python server/manage.py flush
```

#### 3. Problemas de Static Files
```bash
# Coletar static files manualmente
railway run python server/manage.py collectstatic --noinput

# Verificar configuração do WhiteNoise
railway run python server/manage.py check --deploy
```

#### 4. Problemas de Memória/Performance
```bash
# Verificar uso de recursos
railway metrics

# Otimizar workers do Gunicorn
# No Procfile, ajustar:
web: cd server && gunicorn email_classifier.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --max-requests 1000
```

### 5. Debugging Remoto

```bash
# Acessar shell Django remotamente
railway run python server/manage.py shell

# Executar comandos específicos
railway run python server/manage.py check
railway run python server/manage.py showmigrations
```

## Custos e Limites

### Railway Free Tier
- **CPU**: 500 horas/mês
- **RAM**: 512MB
- **Storage**: 1GB
- **Bandwidth**: 100GB/mês
- **Databases**: 1 PostgreSQL (500MB)

### Railway Pro Tier
- **CPU**: Ilimitado
- **RAM**: Configurável
- **Storage**: Configurável
- **Bandwidth**: Ilimitado
- **Databases**: Ilimitadas

### Otimização de Custos
```python
# Configurar sleep mode para desenvolvimento
# No dashboard: Settings → Sleep Mode → Enable

# Monitorar uso
railway metrics --service web
railway metrics --service postgresql
```

## URLs Importantes

Após o deploy, sua aplicação estará disponível em:
- **App Principal**: `https://seu-app.railway.app/`
- **API Status**: `https://seu-app.railway.app/api/status/`
- **Admin**: `https://seu-app.railway.app/admin/`
- **Documentação**: `https://jonhvmp.github.io/email_classifier/`

```bash
# Obter URL da aplicação
railway domain
```
