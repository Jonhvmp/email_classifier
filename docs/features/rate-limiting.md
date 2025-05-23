# Sistema de Rate Limiting

## Visão Geral

O sistema de rate limiting controla o uso de APIs externas para evitar exceção de limites e custos desnecessários.

## RateLimiter Class

### Configuração
```python
gemini_limiter = RateLimiter(
    requests_per_minute=20,    # 60 no free tier, usando 20 para folga
    requests_per_day=15000,    # 60000 no free tier, usando 15000 para folga
    name="gemini"
)
```

### Funcionamento

#### Controles Implementados
- **Por minuto**: Máximo de requisições em janela deslizante de 60s
- **Por dia**: Máximo de requisições do início ao fim do dia
- **Thread-safe**: Uso de `threading.RLock()`

#### Estruturas de Dados
```python
self.minute_requests = []  # Timestamps das últimas requisições
self.day_requests = []     # Todas as requisições do dia
self.total_requests_today = 0   # Contador total
self.day_start = datetime.now().replace(hour=0, minute=0, second=0)
```

## Métodos Principais

### `can_make_request()`
Verifica se uma nova requisição pode ser feita.

#### Retorno
```python
can_request, wait_time = limiter.can_make_request()
# can_request: bool - Se pode fazer requisição
# wait_time: int - Segundos para esperar se não pode
```

#### Lógica
1. Remove requisições antigas (> 1 minuto)
2. Verifica limite por minuto
3. Verifica limite diário
4. Calcula tempo de espera necessário

### `wait_if_needed()`
Método principal usado pelo sistema.

#### Comportamento
```python
can_proceed = limiter.wait_if_needed()
if can_proceed:
    # Fazer requisição para API
    result = api_call()
else:
    # Usar fallback ou rejeitar
    result = fallback_method()
```

#### Estratégias de Espera
- **< 5 minutos**: Espera o tempo necessário
- **> 5 minutos**: Rejeita e usa fallback
- **Novo dia**: Reset automático dos contadores

### `get_stats()`
Retorna estatísticas de uso atual.

#### Retorno
```python
{
    "name": "gemini",
    "minute_usage": 5,
    "minute_limit": 20,
    "minute_percent": 25.0,
    "day_usage": 150,
    "day_limit": 15000,
    "day_percent": 1.0,
    "total_today": 150
}
```

## Integração com AI Service

### Verificação Antes da Chamada
```python
def classify_email(subject, content):
    if not GEMINI_API_KEY:
        return _heuristic_classification(subject, content)

    # Verificar rate limiting
    if not gemini_limiter.wait_if_needed():
        logger.warning("Rate limit excedido, usando classificação heurística.")
        return _heuristic_classification(subject, content)

    # Prosseguir com API Gemini
    model = genai.GenerativeModel(text_model)
    response = model.generate_content(prompt)

    # Log de estatísticas
    stats = gemini_limiter.get_stats()
    logger.info(f"Uso da API: {stats['day_usage']}/{stats['day_limit']} ({stats['day_percent']:.1f}%)")
```

### Logging e Monitoramento
```python
# Alerta quando próximo do limite
if self.total_requests_today > self.requests_per_day * 0.8:
    logger.warning(f"Aproximando-se do limite diário: {self.total_requests_today}/{self.requests_per_day}")

# Log de cada requisição
logger.debug(f"Requisição registrada: {self.total_requests_minute}/{self.requests_per_minute} req/min")
```

## Limites da API Gemini

### Free Tier (Padrão)
- **Por minuto**: 60 requisições
- **Por dia**: 60.000 requisições

### Configuração Conservadora (Aplicada)
- **Por minuto**: 20 requisições (33% do limite)
- **Por dia**: 15.000 requisições (25% do limite)

## Sistema de Fallback

### Quando Rate Limit é Atingido
1. **Log warning** sobre limite atingido
2. **Usar classificação heurística** baseada em palavras-chave
3. **Manter funcionalidade** do sistema
4. **Continuar monitoramento** para quando limite resetar

### Classificação Heurística
```python
def _heuristic_classification(subject, content):
    """Fallback quando API não disponível"""
    text_lower = (subject + " " + content).lower()

    # Palavras-chave para cada categoria
    improdutivo_count = sum(1 for k in improdutivo_keywords if k in text_lower)
    produtivo_count = sum(1 for k in produtivo_keywords if k in text_lower)

    # Regras especiais
    if "reunião" in text_lower and "confirmar" in text_lower:
        return 'productive'

    # Decisão baseada em contagem
    return 'unproductive' if improdutivo_count > produtivo_count else 'productive'
```

## Monitoramento via API

### Endpoint `/api/usage/`
Retorna estatísticas em tempo real:

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
  "timestamp": "2023-12-01T10:30:00Z"
}
```

## Reset Automático

### Diário (Meia-noite)
```python
def _is_new_day(self):
    now = datetime.now()
    if now >= self.day_end:
        logger.info("Novo dia iniciado, resetando contadores")
        self.day_requests = []
        self.reset_day_stats()
        return True
    return False
```

### Por Minuto (Janela Deslizante)
```python
def _cleanup_old_requests(self):
    now = time.time()
    minute_ago = now - 60
    self.minute_requests = [t for t in self.minute_requests if t > minute_ago]
```
