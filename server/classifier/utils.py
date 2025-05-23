import os
import re
from PyPDF2 import PdfReader
from datetime import datetime

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s@.,;:?!-]', '', text)
    return text.strip()

def extract_text_from_file(file_path):
    """
    Extract text from various file types.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (subject, content, sender)
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return extract_from_pdf(file_path)
    elif file_extension == '.txt':
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_from_pdf(file_path):
    """Extract text from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        from .ai_service import process_document
        result = process_document(text, 'pdf')

        return (
            result.get('subject', 'No Subject'),
            result.get('content', text),
            result.get('sender', 'noreply@example.com')
        )
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        filename = os.path.basename(file_path)
        return (filename, f"Failed to process PDF content: {str(e)}", "noreply@example.com")

def extract_from_txt(file_path):
    """Extract text from text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()

        from .ai_service import process_document
        result = process_document(text, 'txt')

        return (
            result.get('subject', 'No Subject'),
            result.get('content', text),
            result.get('sender', 'noreply@example.com')
        )
    except Exception as e:
        print(f"Error extracting text from TXT: {str(e)}")
        filename = os.path.basename(file_path)
        return (filename, f"Failed to process text content: {str(e)}", "noreply@example.com")

def extract_sender(text):
    """Extrai possível remetente do texto"""
    sender_patterns = [
        r'De:\s*([\w\.-]+@[\w\.-]+\.\w+)',
        r'From:\s*([\w\.-]+@[\w\.-]+\.\w+)',
        r'Remetente:\s*([\w\.-]+@[\w\.-]+\.\w+)',
        r'Email:\s*([\w\.-]+@[\w\.-]+\.\w+)',
        r'[\w\.-]+@[\w\.-]+\.\w+'
    ]

    for pattern in sender_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return ""

def extract_subject(text):
    """Extrai possível assunto do texto"""
    subject_patterns = [
        r'Assunto:\s*(.*?)(?:\n|$)',
        r'Subject:\s*(.*?)(?:\n|$)',
        r'Re:\s*(.*?)(?:\n|$)',
        r'Fwd:\s*(.*?)(?:\n|$)'
    ]

    for pattern in subject_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    words = text.split()
    return ' '.join(words[:5]) + '...' if len(words) > 5 else text[:50]

def clean_content(text, subject="", sender=""):
    """Limpa o conteúdo removendo cabeçalhos e informações de remetente"""
    content = text

    patterns_to_remove = [
        r'De:.*\n',
        r'Para:.*\n',
        r'Enviado em:.*\n',
        r'Assunto:.*\n',
        r'Subject:.*\n',
        r'From:.*\n',
        r'To:.*\n',
        r'Sent:.*\n',
        r'Date:.*\n',
        r'Cc:.*\n',
        r'Cópia:.*\n',
        r'Responder para:.*\n'
    ]

    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content)

    if subject:
        content = content.replace(f"Assunto: {subject}", "")
        content = content.replace(subject, "")

    signature_markers = [
        "--\n",
        "---\n",
        "Atenciosamente,",
        "Att.",
        "Atenciosamente",
        "Regards,",
        "Best regards"
    ]

    for marker in signature_markers:
        parts = content.split(marker, 1)
        if len(parts) > 1:
            content = parts[0]

    # Limpa espaços em branco duplicados
    content = re.sub(r'\n\s*\n', '\n\n', content)

    return content.strip()

def get_timestamp():
    """Retorna um timestamp formatado para uso em nomes de arquivos"""
    return datetime.now().strftime("%Y%m%d%H%M%S")

def smart_truncate(text, max_length, suffix="..."):
    """
    Trunca texto de forma inteligente, tentando quebrar em palavras
    """
    if not text:
        return ''
    if len(text) <= max_length:
        return text

    # Se o texto for muito longo, tenta truncar na última palavra completa
    truncated = text[:max_length - len(suffix)]
    last_space_index = truncated.rfind(' ')

    # Se encontrou um espaço e não está muito próximo do início
    if last_space_index > max_length * 0.7:
        return truncated[:last_space_index] + suffix

    # Caso contrário, trunca no limite exato
    return truncated + suffix

def format_text_for_display(text, max_length=200):
    """
    Formata texto para exibição, removendo quebras de linha excessivas e truncando
    """
    if not text:
        return ''

    # Normalizar espaços em branco
    text = ' '.join(text.split())

    # Truncar se necessário
    return smart_truncate(text, max_length)
