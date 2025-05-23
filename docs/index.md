# Email Classifier System

## Visão Geral

O Email Classifier System é uma aplicação Django para classificação automática de emails como **produtivos** ou **improdutivos** utilizando Inteligência Artificial. O sistema foi desenvolvido como case para vaga de Engenheiro de Software Jr.

## Principais Funcionalidades

### 🤖 Classificação Inteligente
- Classificação automática usando Google Gemini AI
- Fallback heurístico quando a API não está disponível
- Sistema de confiança para classificações

### 📄 Processamento de Documentos
- Upload e processamento de arquivos PDF e TXT
- Extração automática de assunto, conteúdo e remetente
- Suporte a múltiplos formatos de entrada

### 🚀 Sistema de Filas
- Processamento assíncrono de emails
- Sistema de prioridades para jobs
- Monitoramento de status em tempo real

### ⚡ Rate Limiting
- Controle de requisições por minuto e por dia
- Proteção contra overuse das APIs
- Estatísticas de uso em tempo real

### 🌐 API RESTful
- Endpoints para submissão e consulta
- Suporte a CORS para frontends
- Documentação completa dos endpoints

## Tecnologias Utilizadas

- **Backend**: Django 4.2+
- **IA**: Google Gemini AI
- **Banco de Dados**: SQLite (desenvolvimento)
- **Upload**: PDF/TXT processing
- **Documentação**: MkDocs Material

## Estrutura do Projeto

```
server/
├── classifier/           # App principal
│   ├── models.py        # Modelos de dados
│   ├── views.py         # Views e APIs
│   ├── ai_service.py    # Serviços de IA
│   ├── job_queue.py     # Sistema de filas
│   └── rate_limiter.py  # Rate limiting
├── email_classifier/    # Configurações Django
└── requirements.txt     # Dependências
```

## Primeiros Passos

1. **Instalação**: Consulte o [Guia de Instalação](setup/installation.md)
2. **Configuração**: Configure as [Variáveis de Ambiente](setup/environment.md)
3. **Arquitetura**: Entenda a [Visão Geral](architecture/overview.md)
4. **APIs**: Explore os [Endpoints Disponíveis](architecture/apis.md)
