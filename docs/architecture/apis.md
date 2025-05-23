# APIs e Endpoints

## Endpoints Disponíveis

### Web Interface

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET/POST | Página inicial com formulário |
| `/emails/` | GET | Lista de emails classificados |
| `/emails/<id>/` | GET | Detalhes de um email |
| `/about/` | GET | Sobre o projeto |

### REST API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/status/` | GET | Status da API |
| `/api/submit-email/` | POST | Submeter email para classificação |
| `/api/emails/` | GET | Lista emails em JSON |
| `/api/emails/<id>/` | GET | Detalhes de email em JSON |
| `/api/usage/` | GET | Estatísticas de uso |
| `/api/jobs/<job_id>/` | GET | Status de job específico |

## Detalhes dos Endpoints

### POST /api/submit-email/

Submete um email para classificação assíncrona.

#### Request
```json
{
  "input_method": "text|file",
  "subject": "Assunto do email",
  "content": "Conteúdo do email",
  "sender": "user@example.com",
  "file": "<arquivo em base64>",
  "use_file_subject": true,
  "use_file_sender": true
}
```

#### Response (Sucesso)
```json
{
  "status": "queued",
  "message": "Email submetido para processamento",
  "id": 123,
  "job_id": "uuid-do-job",
  "queue_position": 2,
  "estimated_wait": 6,
  "queue_status": {
    "queue_length": 2,
    "estimated_wait": 6,
    "processing_count": 1
  }
}
```

#### Response (Erro)
```json
{
  "status": "error",
  "message": "Descrição do erro",
  "errors": {"field": ["erro específico"]}
}
```

### GET /api/jobs/{job_id}/

Verifica o status de processamento de um job.

#### Response (Processando)
```json
{
  "id": "uuid-do-job",
  "job_type": "process_email_complete",
  "status": "processing",
  "created_at": "2023-12-01T10:00:00Z",
  "started_at": "2023-12-01T10:00:05Z",
  "position_in_queue": 0,
  "estimated_wait_time": 0
}
```

#### Response (Concluído)
```json
{
  "id": "uuid-do-job",
  "job_type": "process_email_complete",
  "status": "completed",
  "created_at": "2023-12-01T10:00:00Z",
  "started_at": "2023-12-01T10:00:05Z",
  "completed_at": "2023-12-01T10:00:08Z",
  "processing_time": 3.2,
  "email": {
    "id": 123,
    "subject": "Assunto do email",
    "category": "productive",
    "confidence_score": 85.5,
    "is_processed": true
  }
}
```

### GET /api/usage/

Obtém estatísticas de uso das APIs.

#### Response
```json
{
  "gemini_api": {
    "minute_usage": 5,
    "minute_limit": 20,
    "minute_percent": 25.0,
    "day_usage": 150,
    "day_limit": 15000,
    "day_percent": 1.0,
    "total_today": 150
  },
  "job_queue": {
    "queue_length": 2,
    "estimated_wait": 6,
    "processing_count": 1,
    "queued_jobs": [...]
  },
  "timestamp": "2023-12-01T10:30:00Z"
}
```

### GET /api/emails/{id}/

Obtém detalhes de um email específico.

#### Response
```json
{
  "id": 123,
  "subject": "Reunião de alinhamento do projeto",
  "content": "Gostaria de agendar uma reunião...",
  "sender": "manager@empresa.com",
  "category": "productive",
  "suggested_response": "Prezado(a),\n\nAgradeço pelo convite...",
  "created_at": "2023-12-01T10:00:00.000Z",
  "confidence_score": 85.5
}
```

## CORS Configuration

O sistema está configurado para aceitar requisições cross-origin:

- **Access-Control-Allow-Origin**: `*` (desenvolvimento)
- **Access-Control-Allow-Methods**: GET, POST, OPTIONS
- **Access-Control-Allow-Headers**: Content-Type, X-Requested-With

## Rate Limiting

As APIs respeitam os seguintes limites:

- **Gemini API**: 20 req/min, 15000 req/dia
- **Rate limiting**: Implementado via middleware personalizado
- **Fallback**: Sistema heurístico quando limites são atingidos
