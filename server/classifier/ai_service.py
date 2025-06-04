import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import logging
import random
from .rate_limiter import RateLimiter
from .job_queue import job_queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
logger.info(f"GEMINI_API_KEY encontrada: {'Sim' if GEMINI_API_KEY else 'Não'}")

# Criar rate limiter para a API do Gemini
# 60 req/min e 60000 req/dia são os limites padrão para Google Gemini Free Tier
# Vamos usar limites mais conservadores para garantir
gemini_limiter = RateLimiter(
    requests_per_minute=20,  # 60 no free tier, usando 20 para folga
    requests_per_day=15000,  # 60000 no free tier, usando 15000 para folga
    name="gemini"
)

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("API Gemini configurada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar API Gemini: {str(e)}")
else:
    logger.warning("Chave API do Gemini não encontrada, usando fallback para todas as operações")

# Global variable to store classification confidence
classification_confidence = 0.0

# Set up models - usando versão mais recente do modelo
text_model = "gemini-1.5-flash"    # For basic classification and responses
pro_model = "gemini-1.5-pro"       # For more complex reasoning tasks
document_model = "gemini-1.5-flash"  # For document processing

def classify_email(subject, content):
    """
    Classifies an email as productive or unproductive using Gemini AI.
    """
    global classification_confidence

    full_content = f"Assunto: {subject}\n\nConteúdo: {content}"

    prompt = f"""
    Analise o seguinte email e classifique-o como:
    - 'productive' (emails que requerem ação, contêm problemas, perguntas, solicitações, questões técnicas ou assuntos relacionados ao trabalho)
    - 'unproductive' (emails de parabéns, notas de agradecimento, boletins informativos, convites, elogios)

    Email para analisar:
    {full_content}

    Regras para classificação:
    - Emails sobre reuniões, agendamentos ou disponibilidade devem sempre ser classificados como 'productive'
    - Emails com problemas técnicos, solicitações de suporte ou perguntas são 'productive'
    - Emails contendo principalmente elogios, parabéns ou conteúdo social são 'unproductive'
    - Em caso de dúvida, incline-se para a classificação 'productive'

    Responda APENAS com "productive" ou "unproductive" e inclua um valor de confiança de 0-100.
    Formato: "classificação|valor_confiança"
    """

    try:
        if not GEMINI_API_KEY:
            logger.warning("API key do Gemini não está configurada. Usando classificação heurística.")
            return _heuristic_classification(subject, content)

        # Verificar rate limiting antes de fazer a chamada
        if not gemini_limiter.wait_if_needed():
            logger.warning("Rate limit excedido para o Gemini API, usando classificação heurística.")
            return _heuristic_classification(subject, content)

        model = genai.GenerativeModel(text_model)
        logger.info(f"Iniciando classificação com modelo {text_model}")
        response = model.generate_content(prompt)

        # Log de estatísticas de uso
        stats = gemini_limiter.get_stats()
        logger.info(f"Uso da API Gemini: {stats['day_usage']}/{stats['day_limit']} requisições hoje ({stats['day_percent']:.1f}%)")

        logger.info(f"Resposta bruta da IA para classificação: {response.text}")

        classification_text = response.text.strip()

        parts = classification_text.split('|')
        if len(parts) == 2:
            category = parts[0].strip().lower()
            try:
                confidence = float(parts[1].strip())
                classification_confidence = confidence
            except ValueError:
                classification_confidence = 75.0
        else:
            if "productive" in classification_text.lower():
                category = "productive"
            else:
                category = "unproductive"
            classification_confidence = 75.0

        logger.info(f"Categoria detectada: {category} com confiança {classification_confidence}")
        return category

    except Exception as e:
        logger.error(f"Error classifying email with Gemini: {str(e)}")
        return _heuristic_classification(subject, content)

def _heuristic_classification(subject, content):
    """
    Fallback classification method using keyword heuristics.
    """
    global classification_confidence
    classification_confidence = 75.0

    logger.info("Usando classificação heurística baseada em palavras-chave")

    text_lower = (subject + " " + content).lower()

    improdutivo_keywords = [
        "parabéns", "feliz", "aniversário", "congratulações",
        "agradecimento", "obrigado", "newsletter", "informativo",
        "convite", "festa", "celebração", "elogio", "satisfação"
    ]

    produtivo_keywords = [
        "suporte", "problema", "erro", "bug", "solicitação", "ajuda",
        "dúvida", "sistema", "atualização", "relatório", "urgente",
        "incidente", "falha", "acesso", "login", "senha", "não funciona"
    ]

    if "reunião" in text_lower and ("confirmar" in text_lower or "confirme" in text_lower):
        return 'productive'

    improdutivo_count = sum(1 for k in improdutivo_keywords if k in text_lower)
    produtivo_count = sum(1 for k in produtivo_keywords if k in text_lower)

    # Para este email específico sobre feedback positivo
    if "impressionado" in text_lower and "satisfação" in text_lower:
        logger.info("Email de feedback positivo detectado via palavras-chave")
        return 'unproductive'

    if improdutivo_count > produtivo_count:
        logger.info(f"Classificado como improdutivo: {improdutivo_count} palavras-chave improdutivas vs {produtivo_count} produtivas")
        return 'unproductive'
    else:
        logger.info(f"Classificado como produtivo: {produtivo_count} palavras-chave produtivas vs {improdutivo_count} improdutivas")
        return 'productive'

# Funções de detecção de contexto para a geração de resposta
def _is_meeting_related(subject, content):
    text_lower = (subject + " " + content).lower()
    meeting_keywords = ["reunião", "agenda", "disponibilidade", "confirmar", "encontro",
                       "disponível", "horário", "amanhã", "planejamento", "convite",
                       "participação", "presença", "sala de conferência", "videoconferência"]
    return any(keyword in text_lower for keyword in meeting_keywords)

def _is_tech_support_related(subject, content):
    text_lower = (subject + " " + content).lower()
    tech_keywords = ["suporte", "problema", "erro", "bug", "falha", "não funciona",
                    "técnico", "sistema", "aplicativo", "software", "login", "senha",
                    "acesso", "página", "site", "conexão", "internet", "rede"]
    return any(keyword in text_lower for keyword in tech_keywords)

def _is_project_related(subject, content):
    text_lower = (subject + " " + content).lower()
    project_keywords = ["projeto", "atualização", "status", "progresso", "desenvolvimento",
                      "cronograma", "prazo", "entrega", "milestone", "fase", "etapa"]
    return any(keyword in text_lower for keyword in project_keywords)

def _is_request_related(subject, content):
    text_lower = (subject + " " + content).lower()
    request_keywords = ["solicito", "solicitar", "solicitação", "pedir", "peço", "requerer",
                       "requisição", "favor", "poderia", "gostaria", "preciso", "necessito"]
    return any(keyword in text_lower for keyword in request_keywords)

def _contains_feedback(subject, content):
    text_lower = (subject + " " + content).lower()
    feedback_keywords = ["feedback", "opinião", "avaliação", "satisfação", "experiência",
                       "impressão", "achei", "penso", "considero", "sugestão"]
    return any(keyword in text_lower for keyword in feedback_keywords)

def suggest_response(subject, content, category):
    """
    Gera uma resposta sugerida para o email usando Gemini AI.
    """
    # Detectar o contexto do email
    is_meeting_context = _is_meeting_related(subject, content)
    is_tech_support = _is_tech_support_related(subject, content)
    is_project_update = _is_project_related(subject, content)
    is_request = _is_request_related(subject, content)
    is_feedback = _contains_feedback(subject, content)

    context_type = "geral"
    if is_meeting_context:
        context_type = "reunião"
    elif is_tech_support:
        context_type = "suporte técnico"
    elif is_project_update:
        context_type = "projeto"
    elif is_request:
        context_type = "solicitação"
    elif is_feedback:
        context_type = "feedback"

    logger.info(f"Gerando resposta para email - categoria: {category}, contexto: {context_type}")

    if not GEMINI_API_KEY:
        logger.warning("API key do Gemini não está configurada. Usando resposta pré-definida.")
        return _fallback_response(category, is_meeting_context, context_type)

    # Verificar rate limiting antes de fazer a chamada
    if not gemini_limiter.wait_if_needed():
        logger.warning("Rate limit excedido para o Gemini API, usando resposta pré-definida.")
        return _fallback_response(category, is_meeting_context, context_type)

    # Criar prompt baseado no contexto e categoria
    if category == 'unproductive':
        prompt = f"""
        Você é um assistente de atendimento profissional. Crie uma resposta formal para este email que contém feedback positivo/elogio:

        Assunto: {subject}
        Conteúdo: {content}

        Regras para sua resposta:
        - Reconheça educadamente o feedback positivo com detalhes específicos mencionados no email
        - Mantenha um tom formal e profissional mas amigável
        - Use linguagem simples e direta
        - NÃO repita ou parafraseie o conteúdo original
        - Inclua saudação "Prezado(a) [Nome se disponível]," e assinatura "Atenciosamente, Equipe de Atendimento"
        - Responda em português usando português brasileiro formal
        - Entre 3-5 linhas de conteúdo (não muito curto, não muito longo)
        - Expresse gratidão pelo feedback e valorize a opinião do cliente
        """
    elif is_meeting_context:
        prompt = f"""
        Você é um assistente profissional. Crie uma resposta formal para este email sobre reunião/agendamento:

        Assunto: {subject}
        Conteúdo: {content}

        Regras para sua resposta:
        - Confirme o recebimento do email sobre a reunião com detalhes específicos (data, hora, assunto da reunião)
        - Confirme sua presença/participação na reunião mencionada
        - Mencione detalhes importantes que foram incluídos no email (como pauta, documentos, local)
        - Demonstre proatividade e profissionalismo
        - Ofereça-se para contribuir ou trazer informações específicas se aplicável
        - Use linguagem formal e profissional
        - Inclua saudação "Prezado(a) [Nome se disponível]," e assinatura "Atenciosamente, [Seu Nome]"
        - Responda em português usando português brasileiro formal
        - Entre 4-7 linhas de conteúdo para cobrir os principais pontos
        """
    elif is_tech_support:
        prompt = f"""
        Você é um representante de suporte técnico profissional. Crie uma resposta formal para este email contendo uma questão técnica:

        Assunto: {subject}
        Conteúdo: {content}

        Regras para sua resposta:
        - Agradeça pelo contato e reconheça o problema específico relatado
        - Demonstre empatia quanto ao problema técnico enfrentado
        - Informe que a equipe técnica está analisando o problema reportado
        - Forneça um prazo estimado para retorno (ex: 24-48 horas úteis)
        - Se houver soluções temporárias óbvias, sugira-as brevemente
        - Solicite informações adicionais se necessário para diagnóstico
        - Inclua um número de protocolo fictício para acompanhamento
        - Inclua saudação "Prezado(a) [Nome se disponível]," e assinatura "Atenciosamente, Equipe de Suporte Técnico"
        - Responda em português usando português brasileiro formal
        - Entre 5-8 linhas de conteúdo para demonstrar atenção ao caso
        """
    elif is_project_update:
        prompt = f"""
        Você é um gerente de projetos profissional. Crie uma resposta formal para este email sobre atualização de projeto:

        Assunto: {subject}
        Conteúdo: {content}

        Regras para sua resposta:
        - Agradeça pela atualização/informação sobre o projeto
        - Reconheça pontos específicos mencionados no email
        - Demonstre engajamento com o progresso do projeto
        - Ofereça assistência ou recursos adicionais se necessário
        - Mencione próximos passos ou expectativas futuras
        - Use linguagem formal e profissional
        - Inclua saudação "Prezado(a) [Nome se disponível]," e assinatura "Atenciosamente, [Seu Nome]"
        - Responda em português usando português brasileiro formal
        - Entre 4-7 linhas de conteúdo para cobrir os pontos principais
        """
    else:
        prompt = f"""
        Você é um assistente administrativo profissional. Crie uma resposta formal para este email de solicitação:

        Assunto: {subject}
        Conteúdo: {content}

        Regras para sua resposta:
        - Agradeça pelo contato e reconheça a natureza específica da solicitação
        - Confirme o recebimento e entendimento do pedido/questão
        - Informe que a solicitação foi encaminhada para análise pela equipe responsável
        - Forneça um prazo estimado para retorno (ex: 24-48 horas úteis)
        - Ofereça canal adicional de contato em caso de urgência (ex: telefone fictício)
        - Use tom profissional, prestativo e atencioso
        - Termine com uma frase cordial de encerramento
        - Inclua saudação "Prezado(a) [Nome se disponível]," e assinatura "Atenciosamente, Equipe de Atendimento"
        - Responda em português usando português brasileiro formal
        - Entre 4-6 linhas de conteúdo para demonstrar atenção adequada
        """

    try:
        logger.info("Enviando prompt para a API Gemini")

        model = genai.GenerativeModel(text_model)
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Log de estatísticas de uso
        stats = gemini_limiter.get_stats()
        logger.info(f"Uso da API Gemini: {stats['day_usage']}/{stats['day_limit']} requisições hoje ({stats['day_percent']:.1f}%)")

        logger.info("Resposta recebida da API Gemini")

        processed_response = post_process_response(response.text, category, is_meeting_context, context_type)

        return processed_response

    except Exception as e:
        logger.error(f"Erro ao gerar resposta com Gemini: {str(e)}")
        return _fallback_response(category, is_meeting_context, context_type)

def post_process_response(response, category=None, is_meeting=False, context_type="geral"):
    """
    Ensures response is well-formatted, professional and relevant.
    """
    if not response:
        return _fallback_response(category, is_meeting, context_type)

    # Remove instructions, English phrases, or meta-comments
    lines = [l for l in response.split('\n') if l.strip()]
    cleaned = []
    for l in lines:
        if any(x in l.lower() for x in [
            'note:', 'obs:', '[nota]', 'nota:', 'this response', 'as an ai', 'i am', 'i will', 'here is',
            'segue as instruções', 'espero que isso ajude', 'baseado no', 'sure', 'como solicitado'
        ]):
            continue
        if l.strip().startswith(('-', '*', '#')):
            continue
        cleaned.append(l)
    processed = '\n'.join(cleaned).strip()

    # Ensure greeting and signature
    if not any(g in processed.lower() for g in ["prezado", "olá", "caro", "bom dia", "boa tarde", "boa noite"]):
        processed = "Prezado(a),\n\n" + processed

    # Signature based on context
    if is_meeting:
        if not any(s in processed.lower() for s in ["atenciosamente", "cordialmente", "abraços"]):
            processed += "\n\nAtenciosamente,\nMaria Silva"
    elif context_type == "suporte técnico":
        if not any(s in processed.lower() for s in ["atenciosamente", "cordialmente", "abraços", "equipe de suporte"]):
            processed += "\n\nAtenciosamente,\nEquipe de Suporte Técnico"
    elif context_type == "projeto":
        if not any(s in processed.lower() for s in ["atenciosamente", "cordialmente", "abraços"]):
            processed += "\n\nAtenciosamente,\nCarlos Mendes\nGerente de Projetos"
    else:
        if not any(s in processed.lower() for s in ["atenciosamente", "cordialmente", "abraços", "equipe de atendimento"]):
            processed += "\n\nAtenciosamente,\nEquipe de Atendimento"

    # Remove duplicate blank lines
    while "\n\n\n" in processed:
        processed = processed.replace("\n\n\n", "\n\n")

    # Ensure there's a protocol number for support/request emails
    if context_type in ["suporte técnico", "solicitação"] and "protocolo" not in processed.lower():
        protocol_number = f"#{random.randint(100000, 999999)}"
        processed += f"\n\nProtocolo: {protocol_number}"

    return processed

def _fallback_response(category, is_meeting=False, context_type="geral"):
    """
    Provides fallback responses when AI generation fails.
    """
    logger.info(f"Usando resposta de fallback para contexto: {context_type}")

    protocol = f"#{random.randint(100000, 999999)}"

    # Resposta específica para feedback positivo
    if category == 'unproductive':
        return "Prezado(a),\n\nAgradecemos imensamente seu feedback positivo. Ficamos muito felizes em saber que sua experiência com nossos serviços foi satisfatória. Comentários como o seu são extremamente importantes para nós, pois nos motivam a continuar aprimorando nossa plataforma e serviços.\n\nEstamos sempre à disposição para atendê-lo(a).\n\nAtenciosamente,\nEquipe de Atendimento"

    elif is_meeting:
        return "Prezado(a),\n\nAgradeço pelo convite para a reunião. Confirmo minha participação conforme agendado e já reservei o horário em minha agenda. Estou à disposição para contribuir com os tópicos que serão abordados.\n\nCaso haja alguma alteração ou material preparatório para revisão prévia, por favor me informe.\n\nAtenciosamente,\nMaria Silva"

    elif context_type == "suporte técnico":
        return f"Prezado(a),\n\nAgradecemos por entrar em contato com nossa equipe de suporte técnico. Recebemos sua solicitação e compreendemos a situação reportada.\n\nJá encaminhamos seu caso para nossa equipe especializada, que irá analisá-lo com prioridade. Retornaremos com uma solução em até 24 horas úteis.\n\nEm caso de urgência, você também pode nos contatar pelo telefone (11) 3000-0000.\n\nAtenciosamente,\nEquipe de Suporte Técnico\n\nProtocolo: {protocol}"

    elif context_type == "projeto":
        return "Prezado(a),\n\nAgradeço pelo envio da atualização do projeto. As informações compartilhadas são muito importantes para acompanharmos o progresso e garantir que estamos no caminho certo.\n\nFarei a revisão detalhada dos pontos mencionados e, se necessário, agendaremos uma breve reunião para discutirmos os próximos passos.\n\nContinue mantendo a equipe informada sobre qualquer desenvolvimento significativo.\n\nAtenciosamente,\nCarlos Mendes\nGerente de Projetos"

    else:
        return f"Prezado(a),\n\nAgradecemos por entrar em contato. Recebemos sua solicitação e ela foi registrada em nosso sistema.\n\nSua mensagem já foi encaminhada para o departamento responsável, que irá analisá-la e retornar com uma resposta em até 48 horas úteis.\n\nCaso tenha alguma informação adicional relevante, por favor responda a este email mencionando o número de protocolo abaixo.\n\nAtenciosamente,\nEquipe de Atendimento\n\nProtocolo: {protocol}"

def process_document(file_content, file_type):
    """
    Process document content and extract relevant information.
    """
    try:
        if not GEMINI_API_KEY:
            logger.warning("API key do Gemini não está configurada. Usando extração básica.")
            return _extract_basic_info(file_content)

        # Verificar rate limiting antes de fazer a chamada
        if not gemini_limiter.wait_if_needed():
            logger.warning("Rate limit excedido para o Gemini API, usando extração básica.")
            return _extract_basic_info(file_content)

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

        model = genai.GenerativeModel(document_model)
        response = model.generate_content(prompt)

        # Log de estatísticas de uso
        stats = gemini_limiter.get_stats()
        logger.info(f"Uso da API Gemini: {stats['day_usage']}/{stats['day_limit']} requisições hoje ({stats['day_percent']:.1f}%)")

        try:
            response_text = response.text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                extracted_data = json.loads(json_str)

                return {
                    "subject": extracted_data.get("subject", "No subject extracted"),
                    "content": extracted_data.get("content", "No content extracted"),
                    "sender": extracted_data.get("sender", "noreply@example.com")
                }
            else:
                return _extract_basic_info(file_content)

        except json.JSONDecodeError:
            return _extract_basic_info(file_content)

    except Exception as e:
        logger.error(f"Error processing document with Gemini: {str(e)}")
        return _extract_basic_info(file_content)

def _extract_basic_info(text):
    """
    Basic fallback extraction of email parts when AI fails.
    """
    import re

    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_matches = re.findall(email_pattern, text)
    sender = email_matches[0] if email_matches else "noreply@example.com"

    lines = text.strip().split('\n')
    subject = lines[0] if lines else "No Subject"

    content = '\n'.join(lines[1:]) if len(lines) > 1 else text

    return {
        "subject": subject[:100],  # Limit subject length
        "content": content,
        "sender": sender
    }

# Função para atualizar o email no banco quando o job for concluído
def update_email_with_results(email_id, results):
    """
    Atualiza um email no banco de dados com os resultados do processamento de IA

    Args:
        email_id: ID do email no banco de dados
        results: Dicionário com os resultados de classificação (category, confidence_score, suggested_response)
    """
    try:
        # Importar o modelo dentro da função para evitar importação circular
        from .models import Email
        email = Email.objects.get(pk=email_id)

        email.category = results.get('category', 'unknown')
        email.confidence_score = results.get('confidence_score', 0.0)
        email.suggested_response = results.get('suggested_response', '')
        email.save()

        logger.info(f"Email ID {email_id} atualizado com sucesso com os resultados da IA")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar email ID {email_id} com resultados: {str(e)}")
        return False

# Função para processar email completo e atualizar no banco
def process_email_and_update(email_data, email_id):
    """
    Processa um email e atualiza no banco de dados quando concluído

    Args:
        email_data: Dicionário com os dados do email (subject, content, sender)
        email_id: ID do email no banco de dados

    Returns:
        Dicionário com os resultados do processamento
    """
    logger.info(f"Processando email ID {email_id} - Assunto: {email_data.get('subject', '')[:30]}...")

    try:
        # Classificar o email
        category = classify_email(email_data.get('subject', ''), email_data.get('content', ''))

        # Gerar resposta sugerida
        suggested_response = suggest_response(
            email_data.get('subject', ''),
            email_data.get('content', ''),
            category
        )

        results = {
            'category': category,
            'confidence_score': classification_confidence,
            'suggested_response': suggested_response
        }

        # Atualizar no banco de dados
        update_email_with_results(email_id, results)

        return results
    except Exception as e:
        logger.error(f"Erro ao processar email ID {email_id}: {str(e)}")
        # Atualizar com erro no banco
        error_results = {
            'category': 'error',
            'confidence_score': 0.0,
            'suggested_response': f"Erro ao processar: {str(e)}"
        }
        update_email_with_results(email_id, error_results)
        return error_results

# Registra handlers para os diferentes tipos de jobs de IA
def register_ai_handlers():
    """Registrar manipuladores de jobs para operações de IA"""
    job_queue.register_job_type("classify_email", handle_classify_email)
    job_queue.register_job_type("suggest_response", handle_suggest_response)
    job_queue.register_job_type("process_document", handle_process_document)
    job_queue.register_job_type("process_email_complete", handle_process_email_complete)
    logger.info("Manipuladores de jobs de IA registrados")

# Handlers individuais para cada tipo de operação
def handle_classify_email(data):
    """Handler para jobs de classificação de email"""
    subject = data.get('subject', '')
    content = data.get('content', '')
    return {
        'category': classify_email(subject, content),
        'confidence_score': classification_confidence
    }

def handle_suggest_response(data):
    """Handler para jobs de sugestão de resposta"""
    subject = data.get('subject', '')
    content = data.get('content', '')
    category = data.get('category', '')
    return {
        'suggested_response': suggest_response(subject, content, category)
    }

def handle_process_document(data):
    """Handler para jobs de processamento de documento"""
    file_content = data.get('file_content', '')
    file_type = data.get('file_type', '')
    return process_document(file_content, file_type)

# Handler para processamento completo de um email
def handle_process_email_complete(data):
    """Handler para jobs de processamento completo de email"""
    email_data = {
        'subject': data.get('subject', ''),
        'content': data.get('content', ''),
        'sender': data.get('sender', '')
    }
    email_id = data.get('email_id')

    if not email_id:
        raise ValueError("ID do email não fornecido")

    return process_email_and_update(email_data, email_id)

# Função wrapper para processar email usando a fila em vez de processamento direto
def queue_email_processing(email_data):
    """
    Coloca o processamento de email na fila e retorna o ID do job

    Args:
        email_data: Dicionário com subject, content e sender

    Returns:
        ID do job na fila
    """
    job_id = job_queue.enqueue(
        job_type="classify_email",
        data=email_data,
        priority=1
    )

    logger.info(f"Email enfileirado para classificação com job ID: {job_id}")
    return job_id

# Função para enfileirar apenas a geração de resposta
def queue_response_generation(email_data, category):
    """
    Coloca a geração de resposta na fila e retorna o ID do job

    Args:
        email_data: Dicionário com subject, content e sender
        category: Categoria do email ('productive' ou 'unproductive')

    Returns:
        ID do job na fila
    """
    data = {
        'subject': email_data.get('subject', ''),
        'content': email_data.get('content', ''),
        'category': category
    }

    job_id = job_queue.enqueue(
        job_type="suggest_response",
        data=data,
        priority=2  # Prioridade média para geração de resposta
    )

    logger.info(f"Geração de resposta enfileirada com job ID: {job_id}")
    return job_id

# Função para enfileirar processamento de documento
def queue_document_processing(file_content, file_type):
    """
    Coloca o processamento de documento na fila e retorna o ID do job

    Args:
        file_content: Conteúdo do arquivo
        file_type: Tipo do arquivo (ex: 'pdf', 'txt')

    Returns:
        ID do job na fila
    """
    data = {
        'file_content': file_content,
        'file_type': file_type
    }

    job_id = job_queue.enqueue(
        job_type="process_document",
        data=data,
        priority=1  # Alta prioridade para processamento de documento
    )

    logger.info(f"Processamento de documento enfileirado com job ID: {job_id}")
    return job_id

# Função para enfileirar processamento completo de email
def queue_complete_email_processing(email_data, email_id):
    """
    Coloca o processamento completo de email na fila e retorna o ID do job

    Args:
        email_data: Dicionário com subject, content e sender
        email_id: ID do email no banco de dados

    Returns:
        ID do job na fila
    """
    data = {
        'subject': email_data.get('subject', ''),
        'content': email_data.get('content', ''),
        'sender': email_data.get('sender', ''),
        'email_id': email_id
    }

    job_id = job_queue.enqueue(
        job_type="process_email_complete",
        data=data,
        priority=1  # Alta prioridade
    )

    logger.info(f"Email ID {email_id} enfileirado para processamento completo com job ID: {job_id}")
    return job_id

# Função para processar email completo (classificação + resposta) de forma síncrona
# Mantida para compatibilidade com código existente
def process_email(email_data):
    """
    Função principal para processar email (classificação + resposta sugerida)
    Mantida para compatibilidade com código existente
    """
    subject = email_data.get('subject', '')
    content = email_data.get('content', '')

    logger.info(f"Processando email - Assunto: {subject[:50]}...")

    # Classify the email
    category = classify_email(subject, content)
    logger.info(f"Email classificado como: {category}")

    # Generate response
    suggested_response = suggest_response(subject, content, category)
    logger.info(f"Resposta sugerida gerada ({len(suggested_response)} caracteres)")

    return {
        'category': category,
        'confidence_score': classification_confidence,
        'suggested_response': suggested_response
    }

# Registrar handlers quando o módulo for carregado
register_ai_handlers()
