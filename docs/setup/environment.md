# Variáveis de Ambiente

## Arquivo .env

Crie um arquivo `.env` na raiz do projeto server/ com as seguintes variáveis:

```bash
# Django Configuration
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Services
GEMINI_API_KEY=sua-chave-api-gemini

# CORS Configuration
CORS_ORIGIN_FRONT=http://localhost:3000
```

## Variáveis Obrigatórias

### SECRET_KEY
**Descrição**: Chave secreta do Django para criptografia e segurança.
**Exemplo**: `django-insecure-abc123def456...`
**Geração**:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### GEMINI_API_KEY
**Descrição**: Chave de API do Google Gemini para classificação de emails.
**Obtenção**:
1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Crie uma nova API key
3. Configure o projeto e billing se necessário

**Exemplo**: `AIzaSyB1234567890abcdef...`

## Variáveis Opcionais

### DEBUG
**Descrição**: Modo de debug do Django.
**Valores**: `True` ou `False`
**Padrão**: `True`
**Produção**: Sempre `False`

### ALLOWED_HOSTS
**Descrição**: Hosts permitidos para o Django.
**Formato**: Lista separada por vírgulas
**Exemplo**: `localhost,127.0.0.1,meudominio.com`
**Padrão**: `localhost,127.0.0.1`

### CORS_ORIGIN_FRONT
**Descrição**: Origem permitida para requisições CORS do frontend.
**Exemplo**: `http://localhost:3000`
**Padrão**: `http://localhost:3000`

## Configurações de APIs (Legado)

### COHERE_API_KEY
**Descrição**: Chave da API Cohere (não utilizada atualmente).
**Status**: Opcional, mantida para compatibilidade.

### HUGGINGFACE_API_TOKEN
**Descrição**: Token da API Hugging Face (não utilizada atualmente).
**Status**: Opcional, mantida para compatibilidade.

## Validação de Configuração

### No Código
```python
# ai_service.py
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
logger.info(f"GEMINI_API_KEY encontrada: {'Sim' if GEMINI_API_KEY else 'Não'}")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("API Gemini configurada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar API Gemini: {str(e)}")
else:
    logger.warning("Chave API do Gemini não encontrada, usando fallback")
```

### Verificação via Management Command
```bash
python manage.py shell
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Verificar variáveis
print("SECRET_KEY:", "✓" if os.getenv('SECRET_KEY') else "✗")
print("GEMINI_API_KEY:", "✓" if os.getenv('GEMINI_API_KEY') else "✗")
print("DEBUG:", os.getenv('DEBUG', 'True'))
```

## Configuração por Ambiente

### Desenvolvimento
```bash
SECRET_KEY=django-insecure-development-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=sua-chave-de-desenvolvimento
CORS_ORIGIN_FRONT=http://localhost:3000
```

### Produção
```bash
SECRET_KEY=sua-chave-super-secreta-de-producao
DEBUG=False
ALLOWED_HOSTS=domainname.com,www.domainname.com
GEMINI_API_KEY=sua-chave-de-producao
CORS_ORIGIN_FRONT=https://domainname.com
```

### Teste
```bash
SECRET_KEY=test-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
# GEMINI_API_KEY pode ser omitida para usar fallback
CORS_ORIGIN_FRONT=http://localhost:3000
```

## Segurança

### Boas Práticas
- **Nunca committar** o arquivo `.env` no git
- **Usar chaves diferentes** para dev/prod
- **Rotacionar chaves** periodicamente
- **Limitar permissões** das APIs

### .gitignore
Certifique-se que seu `.gitignore` inclua:
```gitignore
# Environment variables
.env
.env.local
.env.production
```

### Backup de Chaves
- Mantenha backup seguro das chaves de produção
- Use serviços de gerenciamento de secrets em produção
- Documente quais chaves são usadas onde
