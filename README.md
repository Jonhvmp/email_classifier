# Email Classifier System

Sistema de classificação automática de emails usando Inteligência Artificial para determinar se são **produtivos** ou **improdutivos**.

## 🤖 Como Funciona

1. **Entrada**: Envie um email via texto direto ou upload de arquivo (PDF/TXT)
2. **Processamento**: IA analisa o conteúdo usando Google Gemini API
3. **Classificação**: Determina se é produtivo (requer ação) ou improdutivo (informativo)
4. **Resposta**: Gera sugestão de resposta personalizada baseada no contexto

## ⚡ Funcionalidades

### 🎯 Classificação Inteligente
- **Google Gemini AI** para análise de conteúdo
- **Fallback heurístico** quando API indisponível
- **Score de confiança** (0-100%) para cada classificação
- **Contexto adaptativo**: reuniões, suporte técnico, projetos, feedback

### 📄 Processamento de Arquivos
- Upload de **PDF** e **TXT**
- Extração automática de assunto, conteúdo e remetente
- Opção de override manual dos campos extraídos

### 🚀 Sistema Assíncrono
- **Fila de processamento** para emails
- **Status em tempo real** via API
- **Priorização** de jobs por tipo

### ⚡ Rate Limiting
- Controle automático de uso da API (20 req/min, 15k req/dia)
- **Estatísticas de uso** em tempo real
- **Fallback** automático para método heurístico

### 🌐 API RESTful
- Endpoints para submissão e consulta
- Suporte completo a **CORS**
- Integração fácil com frontends

## 🏗️ Categorias

### Produtivo
Emails que requerem ação ou resposta:
- Problemas técnicos e solicitações de suporte
- Reuniões e agendamentos
- Projetos e atualizações
- Perguntas e solicitações

### Improdutivo
Emails informativos ou sociais:
- Parabéns e felicitações
- Agradecimentos e elogios
- Newsletters e informativos
- Convites sociais

## 🚀 Início Rápido

```bash
# 1. Clonar repositório
git clone https://github.com/jonhvmp/email_classifier.git
cd email_classifier/server

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
GEMINI_API_KEY=sua-chave-api

# 4. Executar
python manage.py migrate
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 📊 APIs Principais

```bash
# Status da API
GET /api/status/

# Submeter email
POST /api/submit-email/

# Status do processamento
GET /api/jobs/{job_id}/

# Estatísticas de uso
GET /api/usage/
```

## 🛠️ Tecnologias

- **Backend**: Django 4.2+
- **IA**: Google Gemini 1.5 Flash
- **Processamento**: PyPDF2, Rate Limiting
- **Deploy**: Railway (recomendado)
- **Docs**: MkDocs Material

## 📖 Documentação Completa

Para documentação detalhada: [Acesse a documentação](https://jonhvmp.github.io/email_classifier/)

---

**Case desenvolvido para vaga de Engenheiro de Software Jr | Jonh Alex**
