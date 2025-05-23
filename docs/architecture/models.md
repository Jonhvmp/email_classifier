# Modelos de Dados

## Model Email

O modelo principal do sistema que representa um email e sua classificação.

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BigAutoField | Chave primária |
| `subject` | CharField(200) | Assunto do email |
| `content` | TextField | Conteúdo completo do email |
| `sender` | EmailField | Email do remetente |
| `file` | FileField | Arquivo enviado (opcional) |
| `file_type` | CharField(10) | Tipo do arquivo (pdf, txt) |
| `category` | CharField(20) | Categoria: 'productive' ou 'unproductive' |
| `suggested_response` | TextField | Resposta sugerida pela IA |
| `created_at` | DateTimeField | Data/hora de criação |
| `confidence_score` | FloatField | Nível de confiança (0-100) |
| `classification_method` | CharField(20) | Método usado: 'gemini' ou 'heuristic' |

### Choices

#### Category
- `productive`: Emails que requerem ação, contêm problemas, perguntas, solicitações
- `unproductive`: Emails de parabéns, agradecimentos, newsletters, convites

### Métodos

#### `category_display`
```python
@property
def category_display(self):
    """Retorna o valor de exibição da categoria"""
    return dict(self._meta.get_field('category').choices).get(self.category, self.category)
```

#### `is_productive`
```python
@property
def is_productive(self):
    return self.category == 'productive'
```

### Índices de Banco

Para otimização de consultas:
- `category`: Filtros por categoria
- `created_at`: Ordenação cronológica
- `sender`: Busca por remetente

### Upload de Arquivos

#### Função `get_upload_path`
```python
def get_upload_path(instance, filename):
    """Define o caminho para upload de arquivos de email"""
    ext = filename.split('.')[-1]
    subject_slug = slugify(instance.subject[:30])
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f'uploads/{instance.sender.split("@")[0]}_{subject_slug}_{timestamp}.{ext}'
```

**Formato do path**: `uploads/{username}_{subject-slug}_{timestamp}.{ext}`

### Validações

- `subject`: Máximo 200 caracteres
- `sender`: Deve ser um email válido
- `file_type`: Apenas 'pdf' ou 'txt' permitidos
- `confidence_score`: Valor entre 0.0 e 100.0

### Meta Options

```python
class Meta:
    verbose_name = 'Email'
    verbose_name_plural = 'Emails'
    ordering = ['-created_at']  # Mais recentes primeiro
```
