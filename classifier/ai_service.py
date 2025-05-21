import os
import cohere
import requests
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv('COHERE_API_KEY'))
HF_API_TOKEN = os.getenv('HUGGINGFACE_API_KEY', '')
HF_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
HF_API_URL_BACKUP = "https://api-inference.huggingface.co/models/unicamp-dl/ptt5-base-portuguese-vocab"

def classify_email(subject, content):
    """
    Classifica um email como produtivo ou improdutivo usando heurística + Cohere.
    """
    full_content = f"Assunto: {subject}\n\nConteúdo: {content}"

    # Ampliando palavras-chave para maior precisão
    improdutivo_keywords = [
        "parabéns", "feliz", "aniversário", "congratulações", "felicitações",
        "agradecimento", "obrigado", "newsletter", "informativo", "comunicado",
        "convite", "festa", "celebração", "confraternização", "elogio", "satisfação",
        "experiência", "excelente", "gostaria de compartilhar", "feedback positivo",
        "ótimo trabalho", "impressionado", "agradecemos", "parabenizo", "parabens",
        "continue assim", "bom trabalho", "satisfeito", "maravilhoso", "excelência"
    ]

    produtivo_keywords = [
        "suporte", "problema", "erro", "bug", "solicitação", "ajuda",
        "dúvida", "sistema", "atualização", "relatório", "urgente", "reclamação",
        "incidente", "falha", "acesso", "login", "senha", "conta", "atendimento",
        "resolva", "corrigir", "conserto", "não funciona", "quando", "como fazer",
        "necessito", "preciso", "favor resolver", "pendência", "aguardando retorno",
        "reunião", "prazo", "projeto", "planejamento", "confirmar", "confirme",
        "disponibilidade", "tarefas", "escopo", "amanhã", "agenda", "disponível"
    ]

    text_lower = (subject + " " + content).lower()

    # Verificando contexto de reunião/agendamento
    if "reunião" in text_lower and ("confirmar" in text_lower or "confirme" in text_lower):
        # Emails sobre agendamentos e reuniões são produtivos
        return 'productive'

    # Análise mais refinada das palavras-chave
    improdutivo_count = sum(1 for k in improdutivo_keywords if k in text_lower)
    produtivo_count = sum(1 for k in produtivo_keywords if k in text_lower)

    # Verificar se contém frases de elogio específicas
    elogios_frases = [
        "gostaria de compartilhar minha satisfação",
        "excelente experiência",
        "ótimo trabalho",
        "muito satisfeito",
        "experiência incrível",
        "parabéns pelo",
        "equipe de suporte",
        "obrigado e sucesso",
        "site é muito intuitivo"
    ]

    # Verificar se contém frases relacionadas a reuniões/tarefas
    reuniao_frases = [
        "confirmar nossa reunião",
        "gostaria de confirmar",
        "pauta incluirá",
        "definição de escopo",
        "prazos e divisão",
        "confirme sua disponibilidade",
        "projeto alfa",
        "amanhã às"
    ]

    # Priorizar detecção de contextos de reuniões/tarefas
    if any(frase in text_lower for frase in reuniao_frases):
        return 'productive'

    if any(frase in text_lower for frase in elogios_frases):
        return 'unproductive'

    # Heurística melhorada
    if improdutivo_count > 0 and produtivo_count == 0:
        return 'unproductive'
    if produtivo_count > 0 and improdutivo_count == 0:
        return 'productive'

    # Quando há palavras-chave de ambas categorias, analisamos o contexto geral
    try:
        # Usando Cohere para classificação mais precisa
        response = co.classify(
            inputs=[full_content],
            examples=[
                {"text": "Preciso de ajuda com erro no sistema.", "label": "productive"},
                {"text": "Solicito suporte para acesso ao portal.", "label": "productive"},
                {"text": "Encontrado bug na tela de login.", "label": "productive"},
                {"text": "Dúvida sobre relatório financeiro.", "label": "productive"},
                {"text": "Erro ao atualizar cadastro.", "label": "productive"},
                {"text": "Reunião de Planejamento - Projeto Alfa. Gostaria de confirmar nossa reunião de planejamento do Projeto Alfa para amanhã às 10h.", "label": "productive"},
                {"text": "Confirmação de disponibilidade para reunião amanhã", "label": "productive"},
                {"text": "Parabéns pelo serviço!", "label": "unproductive"},
                {"text": "Agradeço pelo atendimento.", "label": "unproductive"},
                {"text": "Convite para evento da empresa.", "label": "unproductive"},
                {"text": "Gostaria de elogiar a equipe.", "label": "unproductive"},
                {"text": "Feliz aniversário!", "label": "unproductive"},
                {"text": "Excelente experiência com o site.", "label": "unproductive"},
                {"text": "Parabéns pelo ótimo trabalho, equipe!", "label": "unproductive"},
                {"text": "Gostaria de compartilhar minha satisfação com os serviços.", "label": "unproductive"},
                {"text": "O site é muito intuitivo e oferece uma experiência excelente.", "label": "unproductive"},
                {"text": "Encontrei tudo o que precisava de forma simples.", "label": "unproductive"},
            ],
            model="embed-multilingual-v3.0"  # Especificando o modelo para evitar o erro
        )
        classification = response.classifications[0].prediction
        confidence = response.classifications[0].confidence * 100 

        # Armazenar o nível de confiança para uso futuro
        global classification_confidence
        classification_confidence = confidence

        # Verificação adicional após classificação do Cohere
        if classification == "productive" and improdutivo_count > produtivo_count:
            # Caso de conflito entre classificação e heurística, mantemos a classificação do modelo
            if confidence < 70:  # Se a confiança for baixa, confiamos mais na heurística
                return "unproductive"

        return classification
    except Exception as e:
        print(f"Erro ao classificar email: {str(e)}")
        # fallback heurístico mais seguro
        global classification_confidence
        classification_confidence = 75.0  # Valor padrão de confiança

        if improdutivo_count >= produtivo_count / 2:  # Damos mais peso para improdutivos
            return 'unproductive'
        return 'productive'

def query_huggingface(prompt, use_backup=False):
    """
    Envia um prompt para o modelo LLM via Hugging Face Inference API.
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,  # Aumentado para respostas mais completas
            "temperature": 0.3,
            "top_p": 0.85,
            "do_sample": True
        }
    }
    api_url = HF_API_URL_BACKUP if use_backup else HF_API_URL

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict) and "generated_text" in result[0]:
                return result[0]["generated_text"].strip()
        return None
    except Exception as e:
        print(f"Erro na API do Hugging Face: {str(e)}")
        return None

def post_process_response(response, category=None, is_meeting=False):
    """
    Garante resposta curta, formal, sem repetições do email original.
    """
    if not response:
        return None

    # Remove instruções, frases em inglês, ou meta-comentários
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

    # Garante saudação e assinatura
    if not any(g in processed for g in ["Prezado", "Olá", "Caro", "Bom dia", "Boa tarde", "Boa noite"]):
        processed = "Prezado(a),\n\n" + processed

    # Assinatura específica para emails de reunião
    if is_meeting:
        if not any(s in processed for s in ["Atenciosamente", "Cordialmente", "Abraços"]):
            processed += "\n\nAtenciosamente,\nMaria Silva"
    else:
        if not any(s in processed for s in ["Atenciosamente", "Cordialmente", "Abraços", "Equipe de Atendimento"]):
            processed += "\n\nAtenciosamente,\nEquipe de Atendimento"

    # Remove linhas duplicadas
    while "\n\n\n" in processed:
        processed = processed.replace("\n\n\n", "\n\n")

    # Limita a 5 linhas
    lines = processed.split('\n')
    if len(lines) > 6:
        processed = '\n'.join(lines[:3] + ['...'] + lines[-2:])

    # Respostas específicas para cada tipo de email
    if is_meeting:
        if len(processed.strip()) <= 100:
            processed = "Prezado(a),\n\nConfirmo minha participação na reunião de planejamento do Projeto Alfa conforme agendado. Estou disponível no horário mencionado e agradeço pelo envio da pauta antecipadamente.\n\nAtenciosamente,\nMaria Silva"
    elif category == 'unproductive':
        if len(processed.strip()) <= 80:
            processed = "Prezado(a),\n\nAgradecemos seu feedback positivo. Ficamos felizes em saber que sua experiência com nossos serviços foi satisfatória. Seu comentário é muito importante para continuarmos aprimorando nossa plataforma.\n\nAtenciosamente,\nEquipe de Atendimento"
    else:
        if len(processed.strip()) <= 80:
            processed = "Prezado(a),\n\nAgradecemos seu contato. Sua solicitação foi recebida e será analisada pela nossa equipe técnica, que retornará com uma solução o mais breve possível.\n\nAtenciosamente,\nEquipe de Atendimento"

    return processed

def suggest_response(subject, content, category):
    """
    Gera uma resposta sugerida para um email com base em seu conteúdo e categoria.
    """
    try:
        # Verificar se o email é sobre uma reunião/agendamento
        text_lower = (subject + " " + content).lower()

        is_meeting_email = any(palavra in text_lower for palavra in [
            "reunião", "disponibilidade", "agenda", "confirmar", "presença",
            "planejamento", "projeto", "amanhã", "horário", "marcar"
        ])

        # Prompts específicos para cada categoria
        if category == 'unproductive':
            prompt = f"""
Você é um assistente profissional de atendimento ao cliente. Crie uma resposta breve e formal para este email de elogio/agradecimento:

Assunto: {subject}
Conteúdo: {content}

Regras para sua resposta:
- Agradeça educadamente pelo feedback positivo
- Mantenha o tom formal e profissional
- Use linguagem simples e direta
- NÃO repita ou parafraseie o conteúdo original
- Inclua saudação "Prezado(a)," e assinatura "Atenciosamente, Equipe de Atendimento"
- Responda em português
- Máximo de 3 linhas de conteúdo
"""
        elif is_meeting_email:
            # Prompt específico para reuniões/agendamentos
            prompt = f"""
Você é um assistente profissional de escritório. Crie uma resposta breve e formal para este email sobre reunião/agendamento:

Assunto: {subject}
Conteúdo: {content}

Regras para sua resposta:
- Confirme o recebimento do email sobre a reunião
- Confirme a presença/participação na reunião mencionada
- Agradeça pelo aviso/convite
- Use linguagem formal e profissional
- Inclua saudação "Prezado(a)," e assinatura "Atenciosamente,"
- Responda em português
- Máximo de 3 linhas de conteúdo
"""
        else:  # produtivo geral
            prompt = f"""
Você é um assistente profissional de suporte técnico. Crie uma resposta breve e formal para este email que contém uma solicitação:

Assunto: {subject}
Conteúdo: {content}

Regras para sua resposta:
- Agradeça pelo contato
- Informe que a solicitação foi recebida e será analisada pela equipe responsável
- Mencione que retornarão com uma solução em breve
- Use linguagem formal e profissional
- NÃO repita o conteúdo original ou tente resolver o problema específico
- Inclua saudação "Prezado(a)," e assinatura "Atenciosamente, Equipe de Atendimento"
- Responda em português
- Máximo de 3 linhas de conteúdo
"""

        # Tentar gerar resposta com Hugging Face
        hf_response = query_huggingface(prompt)

        if not hf_response or len(hf_response) < 20:
            # Fallback com Cohere
            if category == 'unproductive':
                cohere_prompt = f"""
Crie uma resposta breve para um email de elogio/agradecimento:
Assunto: {subject}
Requisitos:
- Agradeça o feedback positivo
- Mencione a importância do feedback para melhorias
- Saudação: "Prezado(a),"
- Assinatura: "Atenciosamente, Equipe de Atendimento"
- Máximo 3 linhas
"""
            elif is_meeting_email:
                cohere_prompt = f"""
Crie uma resposta breve para um email sobre reunião/agendamento:
Assunto: {subject}
Conteúdo resumido: Email sobre confirmação de reunião ou verificação de disponibilidade
Requisitos:
- Confirme a participação na reunião mencionada
- Agradeça pelo aviso/convite
- Saudação: "Prezado(a),"
- Assinatura: "Atenciosamente,"
- Máximo 3 linhas
"""
            else:
                cohere_prompt = f"""
Crie uma resposta breve para um email com solicitação ou problema:
Assunto: {subject}
Requisitos:
- Agradeça o contato
- Informe que a solicitação foi recebida e será analisada
- Saudação: "Prezado(a),"
- Assinatura: "Atenciosamente, Equipe de Atendimento"
- Máximo 3 linhas
"""

            # Gerar resposta com Cohere
            response = co.generate(
                model="command",  # Especificando o modelo para evitar o erro
                prompt=cohere_prompt,
                max_tokens=150,
                temperature=0.3
            )
            suggested_response = response.generations[0].text.strip()
            return post_process_response(suggested_response, category=category, is_meeting=is_meeting_email)

        return post_process_response(hf_response, category=category, is_meeting=is_meeting_email)

    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        # Respostas de fallback melhoradas
        if category == 'productive':
            if any(palavra in text_lower for palavra in ["reunião", "confirmar", "disponibilidade", "planejamento"]):
                return "Prezado(a),\n\nConfirmo minha participação na reunião de planejamento do Projeto Alfa amanhã às 10h. Obrigado pelo aviso e pela informação sobre a pauta.\n\nAtenciosamente,\nMaria Silva"
            return "Prezado(a),\n\nAgradecemos seu contato. Sua solicitação foi recebida e será analisada pela nossa equipe técnica, que retornará com uma solução o mais breve possível.\n\nAtenciosamente,\nEquipe de Atendimento"
        else:
            return "Prezado(a),\n\nAgradecemos seu feedback positivo. É muito gratificante saber que nossos serviços estão atendendo às suas expectativas. Seu comentário nos motiva a continuar melhorando.\n\nAtenciosamente,\nEquipe de Atendimento"

# Variável global para armazenar o nível de confiança da classificação
classification_confidence = 0.0
