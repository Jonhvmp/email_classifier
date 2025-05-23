# Guia de Instalação

## Pré-requisitos

### Sistema
- **Python**: 3.8 ou superior
- **pip**: Gerenciador de pacotes Python
- **Git**: Para clonagem do repositório

### APIs Externas
- **Google Gemini API**: Para classificação de emails
- Conta Google com acesso ao AI Studio

## Instalação Passo a Passo

### 1. Clonar o Repositório
```bash
git clone https://github.com/jonhvmp/email_classifier.git
cd email_classifier
```

### 2. Criar Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
cd server
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar template
cp .env.example .env

# Editar com suas configurações
# Veja: setup/environment.md
```

### 5. Configurar Banco de Dados
```bash
python manage.py migrate
```

### 6. Criar Superusuário (Opcional)
```bash
python manage.py createsuperuser
```

### 7. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --noinput
```

### 8. Executar Servidor de Desenvolvimento
```bash
python manage.py runserver
```

## Verificação da Instalação

### 1. Acessar Interface Web
Abra http://127.0.0.1:8000/ no navegador

### 2. Testar API
```bash
curl http://127.0.0.1:8000/api/status/
```

**Resposta esperada**:
```json
{
  "status": "online",
  "message": "API está funcionando corretamente",
  "version": "1.0.3"
}
```

### 3. Testar Classificação
1. Acesse a página inicial
2. Digite um email de teste
3. Clique em "Classificar Email"
4. Verifique se retorna categoria e resposta sugerida

## Solução de Problemas

### Erro: ModuleNotFoundError
```bash
# Verificar se o ambiente virtual está ativo
which python

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: API Gemini não configurada
```bash
# Verificar variável de ambiente
python manage.py shell
>>> import os
>>> print(os.getenv('GEMINI_API_KEY'))
```

### Erro: CSRF verification failed
- Verificar configuração CORS
- Adicionar origem em CSRF_TRUSTED_ORIGINS

### Erro: File upload não funciona
```bash
# Verificar configuração de mídia
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
>>> print(settings.MEDIA_URL)
```

## Configuração para Desenvolvimento

### Debug Mode
```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Logging Detalhado
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'classifier': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Hot Reload
O servidor Django tem hot reload automático em modo DEBUG.

## Executar Testes

### Testes Unitários
```bash
python manage.py test
```

### Testes com Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera relatório HTML
```

### Testes Específicos
```bash
# Testar apenas app classifier
python manage.py test classifier

# Testar apenas views
python manage.py test classifier.tests.EmailViewTests
```

## Comandos Úteis

### Migrations
```bash
# Criar novas migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Ver status das migrations
python manage.py showmigrations
```

### Shell Django
```bash
# Acessar shell interativo
python manage.py shell

# Exemplo de uso
>>> from classifier.models import Email
>>> Email.objects.count()
```

### Limpeza
```bash
# Limpar banco de dados
python manage.py flush

# Remover arquivos de migração
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```
