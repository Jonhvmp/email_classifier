import os
import PyPDF2
import re
from datetime import datetime

def extract_text_from_file(file_path):
    """
    Extrai texto de arquivos .txt ou .pdf

    Args:
        file_path (str): Caminho para o arquivo

    Returns:
        tuple: (subject, content, sender) - assunto, conteúdo e remetente extraídos do arquivo
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        return extract_from_txt(file_path)
    elif ext == '.pdf':
        return extract_from_pdf(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {ext}")

def extract_from_txt(file_path):
    """
    Extrai texto de um arquivo .txt

    Args:
        file_path (str): Caminho para o arquivo .txt

    Returns:
        tuple: (subject, content, sender) - assunto, conteúdo e remetente extraídos do arquivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        sender = extract_sender(text)
        subject = extract_subject(text)
        content = clean_content(text, subject, sender)

        return subject, content, sender
    except Exception as e:
        print(f"Erro ao extrair texto do arquivo .txt: {str(e)}")
        return "Erro na extração", f"Não foi possível extrair o texto do arquivo: {str(e)}", ""

def extract_from_pdf(file_path):
    """
    Extrai texto de um arquivo .pdf

    Args:
        file_path (str): Caminho para o arquivo .pdf

    Returns:
        tuple: (subject, content, sender) - assunto, conteúdo e remetente extraídos do arquivo
    """
    try:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        sender = extract_sender(text)
        subject = extract_subject(text)
        content = clean_content(text, subject, sender)

        return subject, content, sender
    except Exception as e:
        print(f"Erro ao extrair texto do arquivo PDF: {str(e)}")
        return "Erro na extração", f"Não foi possível extrair o texto do arquivo PDF: {str(e)}", ""

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

def clean_text(text):
    """
    Realiza pré-processamento básico no texto

    Args:
        text (str): Texto a ser processado

    Returns:
        str: Texto processado
    """
    if not text:
        return ""

    # Remove múltiplos espaços em branco
    text = re.sub(r'\s+', ' ', text)

    # Remove caracteres especiais e mantém apenas letras, números, pontuação básica
    text = re.sub(r'[^\w\s.,!?@:;()\'\"-]', '', text)

    # Remove caracteres repetidos (como '....')
    text = re.sub(r'([.,!?])\1{2,}', r'\1', text)

    return text.strip()

def get_timestamp():
    """Retorna um timestamp formatado para uso em nomes de arquivos"""
    return datetime.now().strftime("%Y%m%d%H%M%S")
