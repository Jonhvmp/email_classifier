import os
import cohere
from dotenv import load_dotenv

# Carregando variáveis de ambiente
load_dotenv()

# Inicializando o cliente Cohere
co = cohere.Client(os.getenv('COHERE_API_KEY'))

def classify_email(subject, content):
    """
    Classifica um email como produtivo ou improdutivo usando a API Cohere.

    Args:
        subject (str): Assunto do email
        content (str): Conteúdo do email

    Returns:
        str: 'productive' ou 'unproductive'
    """
    # Combinando assunto e conteúdo para análise
    full_content = f"Assunto: {subject}\n\nConteúdo: {content}"

    # Palavras-chave que podem indicar emails improdutivos
    improdutivo_keywords = [
        "parabéns", "feliz", "aniversário", "congratulações", "felicitações",
        "agradecimento", "obrigado", "newsletter", "informativo", "comunicado",
        "convite", "festa", "celebração", "confraternização"
    ]

    # Palavras-chave que podem indicar emails produtivos
    produtivo_keywords = [
        "suporte", "problema", "erro", "bug", "solicitação", "ajuda",
        "dúvida", "sistema", "atualização", "relatório", "urgente"
    ]

    # Verificação básica de palavras-chave no assunto e conteúdo
    text_lower = (subject + " " + content).lower()

    # Conta ocorrências de palavras-chave
    improdutivo_count = sum(1 for keyword in improdutivo_keywords if keyword in text_lower)
    produtivo_count = sum(1 for keyword in produtivo_keywords if keyword in text_lower)

    # Regra simples: se tiver mais palavras improdutivas que produtivas
    if improdutivo_count > produtivo_count:
        return 'unproductive'

    try:
        # Usando o modelo de classificação da Cohere como fallback
        response = co.classify(
            model='embed-v3',
            inputs=[full_content],
            examples=[
                # Exemplos de emails produtivos - que requerem ação específica
                {"text": "Problema de acesso ao sistema. Preciso de ajuda para recuperar minha senha.", "label": "productive"},
                {"text": "Solicitação de suporte técnico para configurar o servidor de email.", "label": "productive"},
                {"text": "Bug encontrado na funcionalidade de login, precisamos corrigir urgentemente.", "label": "productive"},
                {"text": "Dúvida sobre como utilizar o módulo de relatórios do sistema.", "label": "productive"},
                {"text": "Erro ao tentar fazer login na plataforma, preciso de ajuda.", "label": "productive"},

                # Exemplos de emails improdutivos - que não necessitam de ação imediata
                {"text": "Feliz aniversário para a equipe! Parabéns pelos 5 anos da empresa.", "label": "unproductive"},
                {"text": "Agradecemos a participação de todos no workshop realizado na semana passada.", "label": "unproductive"},
                {"text": "Newsletter mensal: Confira as novidades da empresa este mês!", "label": "unproductive"},
                {"text": "Convite para a confraternização de final de ano da empresa.", "label": "unproductive"},
                {"text": "Parabéns aos aniversariantes do mês! Felicitações a todos.", "label": "unproductive"},
            ]
        )        # Extrair a classificação da resposta
        classification = response.classifications[0].prediction
        return classification
    except Exception as e:
        print(f"Erro ao classificar email: {str(e)}")
        # Se houver erro na API, usamos apenas a classificação baseada em palavras-chave
        return 'unproductive' if improdutivo_count > 0 else 'productive'

def suggest_response(subject, content, category):
    """
    Gera uma resposta sugerida para um email com base em seu conteúdo e categoria.

    Args:
        subject (str): Assunto do email
        content (str): Conteúdo do email
        category (str): Categoria do email ('productive' ou 'unproductive')

    Returns:
        str: Resposta sugerida
    """
    try:
        # Criar o prompt para geração de resposta
        prompt = f"""
        Crie uma resposta educada e profissional em português para o email abaixo, baseado em sua categoria.

        Assunto: {subject}
        Conteúdo: {content}
        Categoria: {'Produtivo' if category == 'productive' else 'Improdutivo'}

        Para emails produtivos, forneça uma resposta detalhada que aborde as necessidades específicas.
        Para emails improdutivos, forneça uma resposta breve e educada.
        """

        # Usar o modelo de geração da Cohere
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        # Extrair e refinar a resposta gerada
        suggested_response = response.generations[0].text.strip()
        return suggested_response
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        # Respostas padrão em caso de erro
        if category == 'productive':
            return "Obrigado pelo seu email. Estamos analisando sua solicitação e retornaremos em breve com uma resposta detalhada."
        else:
            return "Agradecemos seu contato. Infelizmente, no momento não podemos atender a esta solicitação."
