# Sistema de Upload de Arquivos

## Visão Geral

O sistema permite upload de arquivos PDF e TXT para extração automática de conteúdo de emails.

## Formatos Suportados

### PDF (.pdf)
- Processamento via PyPDF2
- Extração de texto de múltiplas páginas
- Processamento via AI para estruturação

### TXT (.txt)
- Leitura direta com encoding UTF-8
- Fallback para outros encodings
- Processamento via AI para extração de campos

## Configuração de Upload

### Função `get_upload_path`
```python
def get_upload_path(instance, filename):
    """Define o caminho para upload de arquivos de email"""
    ext = filename.split('.')[-1]
    subject_slug = slugify(instance.subject[:30])
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f'uploads/{instance.sender.split("@")[0]}_{subject_slug}_{timestamp}.{ext}'
```

### Estrutura de Diretórios
```
media/
└── uploads/
    ├── user1_meeting-agenda_20231201153045.pdf
    ├── user2_support-request_20231201153102.txt
    └── user3_project-update_20231201153150.pdf
```

### Configurações Django
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Processo de Extração

### 1. Upload e Validação
```python
def clean(self):
    if input_method == 'file':
        if not file:
            self.add_error('file', 'Por favor, faça upload de um arquivo.')

        # Verificar extensão
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.txt', '.pdf']:
            self.add_error('file', 'Apenas arquivos .txt ou .pdf são permitidos.')
```

### 2. Extração de Texto
```python
def extract_text_from_file(file_path):
    """Extract text from various file types"""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return extract_from_pdf(file_path)
    elif file_extension == '.txt':
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
```

### 3. Processamento PDF
```python
def extract_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # Usar AI para estruturação
        result = process_document(text, 'pdf')

        return (
            result.get('subject', 'No Subject'),
            result.get('content', text),
            result.get('sender', 'noreply@example.com')
        )
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        return (filename, f"Failed to process: {str(e)}", "noreply@example.com")
```

### 4. Processamento TXT
```python
def extract_from_txt(file_path):
    """Extract text from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()

        # Usar AI para estruturação
        result = process_document(text, 'txt')

        return (
            result.get('subject', 'No Subject'),
            result.get('content', text),
            result.get('sender', 'noreply@example.com')
        )
    except Exception as e:
        logger.error(f"Error extracting TXT: {str(e)}")
        return (filename, f"Failed to process: {str(e)}", "noreply@example.com")
```

## Processamento com IA

### Prompt para Extração
```python
prompt = f"""
Extract the following information from this email document:
1. Email subject line
2. Email body text
3. Sender email address

Document content:
{file_content}

Respond with only this JSON format:
{{
  "subject": "extracted subject",
  "content": "extracted content",
  "sender": "extracted sender email"
}}
"""
```

### Fallback Heurístico
```python
def _extract_basic_info(text):
    """Basic fallback extraction when AI fails"""
    import re

    # Extrair email
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_matches = re.findall(email_pattern, text)
    sender = email_matches[0] if email_matches else "noreply@example.com"

    # Primeira linha como assunto
    lines = text.strip().split('\n')
    subject = lines[0] if lines else "No Subject"

    # Resto como conteúdo
    content = '\n'.join(lines[1:]) if len(lines) > 1 else text

    return {
        "subject": subject[:100],
        "content": content,
        "sender": sender
    }
```

## Interface do Usuário

### Formulário com Opções
```html
<!-- Radio buttons para escolher método -->
<input type="radio" name="input_method" value="text" checked> Texto direto
<input type="radio" name="input_method" value="file"> Upload de arquivo

<!-- Upload de arquivo -->
<input type="file" name="file" accept=".txt,.pdf">

<!-- Opções de override -->
<input type="checkbox" name="use_file_subject" checked>
Usar campo de assunto acima (ignorar assunto do arquivo)

<input type="checkbox" name="use_file_sender" checked>
Usar campo de remetente acima (ignorar remetente do arquivo)
```

### Lógica de Processamento
```python
if input_method == 'file' and email.file:
    # Salvar arquivo
    email.file.save(email.file.name, email.file, save=True)

    # Extrair dados do arquivo
    subject_from_file, content_from_file, sender_from_file = extract_text_from_file(file_path)

    # Aplicar configurações do usuário
    use_manual_subject = form.cleaned_data.get('use_file_subject', False)
    if not use_manual_subject or not email.subject:
        email.subject = subject_from_file

    use_manual_sender = form.cleaned_data.get('use_file_sender', False)
    if not use_manual_sender:
        email.sender = sender_from_file or extract_email_from_content(content_from_file)

    email.content = content_from_file
```

## Segurança e Validação

### Validações Implementadas
- **Extensão de arquivo**: Apenas .pdf e .txt
- **Tamanho**: Limitado pelo Django (default 2.5MB)
- **Encoding**: UTF-8 com fallback graceful
- **Path traversal**: Prevenido pelo Django FileField

### Limpeza de Arquivos
- **Naming**: Slugify + timestamp para evitar conflitos
- **Storage**: Organizado por usuário e data
- **Cleanup**: Manual via admin ou comando Django

### Tratamento de Erros
```python
try:
    # Processar arquivo
    extracted_data = extract_text_from_file(file_path)
except Exception as e:
    logger.error(f"Erro ao processar arquivo: {str(e)}")
    return JsonResponse({
        'status': 'error',
        'message': f'Erro ao processar o arquivo: {str(e)}'
    }, status=400)
```
