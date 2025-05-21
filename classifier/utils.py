import os
import PyPDF2
import re

def extract_text_from_file(file_path):
    """
    Extrai texto de arquivos .txt ou .pdf

    Args:
        file_path (str): Caminho para o arquivo

    Returns:
        tuple: (subject, content) - assunto e conteúdo extraídos do arquivo
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
        tuple: (subject, content) - assunto e conteúdo extraídos do arquivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Tenta extrair o assunto do texto
        subject = ""
        content = text

        # Procura por padrões comuns de assunto em emails
        subject_patterns = [
            r'Assunto:\s*(.*?)(?:\n|$)',
            r'Subject:\s*(.*?)(?:\n|$)',
            r'Re:\s*(.*?)(?:\n|$)',
            r'Fwd:\s*(.*?)(?:\n|$)'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text)
            if match:
                subject = match.group(1).strip()
                # Remove a linha do assunto do conteúdo
                content = re.sub(pattern, '', text, count=1).strip()
                break

        # Se não encontrou assunto, usa as primeiras palavras como assunto
        if not subject:
            words = text.split()
            subject = ' '.join(words[:5]) + '...' if len(words) > 5 else text

        return subject, content
    except Exception as e:
        print(f"Erro ao extrair texto do arquivo .txt: {str(e)}")
        return "Erro na extração", f"Não foi possível extrair o texto do arquivo: {str(e)}"

def extract_from_pdf(file_path):
    """
    Extrai texto de um arquivo .pdf

    Args:
        file_path (str): Caminho para o arquivo .pdf

    Returns:
        tuple: (subject, content) - assunto e conteúdo extraídos do arquivo
    """
    try:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        # Tenta extrair o assunto do texto
        subject = ""
        content = text

        # Procura por padrões comuns de assunto em emails
        subject_patterns = [
            r'Assunto:\s*(.*?)(?:\n|$)',
            r'Subject:\s*(.*?)(?:\n|$)',
            r'Re:\s*(.*?)(?:\n|$)',
            r'Fwd:\s*(.*?)(?:\n|$)'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text)
            if match:
                subject = match.group(1).strip()
                # Remove a linha do assunto do conteúdo
                content = re.sub(pattern, '', text, count=1).strip()
                break

        # Se não encontrou assunto, usa as primeiras palavras como assunto
        if not subject:
            words = text.split()
            subject = ' '.join(words[:5]) + '...' if len(words) > 5 else text

        return subject, content
    except Exception as e:
        print(f"Erro ao extrair texto do arquivo PDF: {str(e)}")
        return "Erro na extração", f"Não foi possível extrair o texto do arquivo PDF: {str(e)}"

def clean_text(text):
    """
    Realiza pré-processamento básico no texto

    Args:
        text (str): Texto a ser processado

    Returns:
        str: Texto processado
    """
    # Remove múltiplos espaços em branco
    text = re.sub(r'\s+', ' ', text)

    # Remove caracteres especiais e mantém apenas letras, números, pontuação básica
    text = re.sub(r'[^\w\s.,!?@:;()\'\"-]', '', text)

    return text.strip()
