import pytest
from classifier.ai_service import classify_email, suggest_response, post_process_response

def test_classification_heuristics():
    """Testa a classificação baseada em heurísticas."""
    # Email claramente improdutivo
    subject = "Parabéns pelo ótimo trabalho!"
    content = "Estamos muito satisfeitos com o serviço prestado. Obrigado!"
    assert classify_email(subject, content) == 'unproductive'

    # Email claramente produtivo
    subject = "Problema no sistema de login"
    content = "Estou enfrentando um erro ao tentar acessar minha conta."
    assert classify_email(subject, content) == 'productive'

def test_response_generation():
    """Testa a geração de respostas."""
    subject = "Elogios ao serviço"
    content = "Parabéns pelo excelente trabalho e atendimento."
    response = suggest_response(subject, content, 'unproductive')

    # Verifica se a resposta tem formato esperado
    assert "Prezado(a)" in response
    assert "Atenciosamente" in response

    # Verifica se não é uma resposta vazia
    assert len(response) > 30

def test_post_processing():
    """Testa o pós-processamento de respostas."""
    raw_response = """
    I'll respond as requested:

    Prezado cliente,

    Agradecemos seu feedback positivo. Sua opinião é importante para nós.

    Atenciosamente,
    Equipe
    """

    processed = post_process_response(raw_response)

    # Verifica se instruções em inglês foram removidas
    assert "I'll respond as requested" not in processed

    # Verifica se mantém o conteúdo relevante
    assert "Agradecemos seu feedback" in processed
