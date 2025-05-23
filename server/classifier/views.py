from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
import logging
from datetime import datetime
from .models import Email
from .forms import EmailForm
from .utils import extract_text_from_file
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_service import process_email, queue_email_processing, queue_complete_email_processing, gemini_limiter, job_queue
from .job_queue import JobStatus  # Adicionando import faltante

logger = logging.getLogger(__name__)

def home(request):
    """
    View da página inicial com formulário para submissão de email.
    """
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HTTP_ORIGIN' in request.META

        form = EmailForm(request.POST, request.FILES)
        logger.info(f"Processando formulário, é válido? {form.is_valid()}")

        if form.is_valid():
            email = form.save(commit=False)
            input_method = form.cleaned_data.get('input_method')

            if input_method == 'file' and email.file:
                try:
                    email.file.save(email.file.name, email.file, save=True)
                    file_path = email.file.path

                    subject_from_file, content_from_file, sender_from_file = extract_text_from_file(file_path)

                    use_manual_subject = form.cleaned_data.get('use_file_subject', False)
                    if not use_manual_subject or not email.subject:
                        email.subject = subject_from_file

                    use_manual_sender = form.cleaned_data.get('use_file_sender', False)
                    if not use_manual_sender:
                        if sender_from_file:
                            email.sender = sender_from_file
                        else:
                            import re
                            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                            email_matches = re.findall(email_pattern, content_from_file)
                            if email_matches:
                                email.sender = email_matches[0]
                            else:
                                email.sender = 'noreply@example.com'
                    email.content = content_from_file

                except Exception as e:
                    logger.error(f"Erro ao processar arquivo: {str(e)}")
                    if is_ajax:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Erro ao processar o arquivo: {str(e)}'
                        }, status=400)
                    messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
                    return render(request, 'classifier/home.html', {'form': form})

            try:
                logger.info(f"Processando email - Assunto: {email.subject[:30]}...")

                email_data = {
                    'subject': email.subject,
                    'content': email.content,
                    'sender': email.sender
                }

                result = process_email(email_data)

                email.category = result['category']
                email.confidence_score = result['confidence_score']
                email.suggested_response = result['suggested_response']

                logger.info(f"Email processado - Categoria: {email.category}, Confiança: {email.confidence_score:.2f}%")

                email.save()
                logger.info(f"Email salvo com ID: {email.pk}")

                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'id': email.pk,
                        'subject': email.subject,
                        'category': email.category,
                        'confidence_score': email.confidence_score
                    })

                messages.success(request, 'Email classificado com sucesso!')
                return redirect('email_detail', pk=email.pk)

            except Exception as e:
                logger.error(f"ERRO no processamento: {str(e)}")
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao processar o email: {str(e)}'
                    }, status=500)
                messages.error(request, f'Erro ao processar o email: {str(e)}')
                return render(request, 'classifier/home.html', {'form': form})
        else:
            logger.error(f"Form inválido: {form.errors}")
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors.as_json()
                }, status=400)
    else:
        form = EmailForm()

    return render(request, 'classifier/home.html', {'form': form})

class EmailListView(ListView):
    """
    View para listar todos os emails classificados.
    """
    model = Email
    template_name = 'classifier/email_list.html'
    context_object_name = 'emails'
    paginate_by = 10

class EmailDetailView(DetailView):
    """
    View para mostrar os detalhes de um email específico.
    """
    model = Email
    template_name = 'classifier/email_detail.html'
    context_object_name = 'email'

def about(request):
    """
    View da página sobre o projeto.
    """
    return render(request, 'classifier/about.html')

def api_status(request):
    """
    View para verificar o status da API.
    """
    try:
        endpoints = {
            "/": "Página inicial com formulário",
            "/emails/": "Lista de emails classificados",
            "/emails/1/": "Detalhes de um email específico (substitua 1 pelo ID)",
            "/about/": "Sobre o projeto",
            "/api/status/": "Status da API (este endpoint)",
            "/api/submit-email/": "Endpoint para submissão de emails (POST)",
            "/api/emails/": "Lista de todos os emails em formato JSON",
            "/api/emails/1/": "Detalhes de um email específico em JSON (substitua 1 pelo ID)",
            "/api/usage/": "Estatísticas de uso da API"
        }

        logger.info(f"API status chamado, origem: {request.headers.get('origin', 'desconhecida')}")

        # Verificar conexão com banco de dados
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error(f"Erro de conexão com banco: {e}")

        response_data = {
            "status": "online",
            "message": "API está funcionando corretamente",
            "database": db_status,
            "endpoints": endpoints,
            "csrf_required": False,
            "version": "1.0.4"
        }

        response = JsonResponse(response_data)

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept"

        logger.info("✅ API status response enviada com sucesso")
        return response

    except Exception as e:
        logger.error(f"❌ Erro no endpoint api_status: {e}")
        return JsonResponse({
            "status": "error",
            "message": f"Erro interno: {str(e)}"
        }, status=500)

def api_usage(request):
    """
    API para obter estatísticas de uso da API.
    """
    try:
        # Obter estatísticas dos rate limiters
        gemini_stats = gemini_limiter.get_stats()
        queue_stats = job_queue.get_queue_status()

        data = {
            "gemini_api": {
                "minute_usage": gemini_stats["minute_usage"],
                "minute_limit": gemini_stats["minute_limit"],
                "minute_percent": gemini_stats["minute_percent"],
                "day_usage": gemini_stats["day_usage"],
                "day_limit": gemini_stats["day_limit"],
                "day_percent": gemini_stats["day_percent"],
                "total_today": gemini_stats["total_today"]
            },
            "job_queue": queue_stats,
            "timestamp": datetime.now().isoformat()
        }

        response = JsonResponse(data)
        # Adicionar cabeçalhos CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de uso: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def api_submit_email(request):
    """
    Endpoint API para submissão de emails pelo frontend sem verificação CSRF.
    Usa fila para processamento assíncrono.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    logger.info("Recebendo submissão de email via API")

    try:
        form = EmailForm(request.POST, request.FILES)

        if not form.is_valid():
            logger.error(f"Form inválido: {form.errors}")
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.as_json()
            }, status=400)

        # Usar versão assíncrona
        return _process_valid_form_async(form, is_api=True)

    except Exception as e:
        logger.error(f"ERRO geral: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }, status=500)

def _process_valid_form_async(form, is_api=False):
    """
    Processa um formulário válido de forma assíncrona usando a fila.
    """
    email = form.save(commit=False)
    input_method = form.cleaned_data.get('input_method')

    # Processar arquivo se enviado
    if input_method == 'file' and email.file:
        try:
            email.file.save(email.file.name, email.file, save=True)
            file_path = email.file.path

            subject_from_file, content_from_file, sender_from_file = extract_text_from_file(file_path)

            # Aplicar campos do arquivo conforme configurações
            use_manual_subject = form.cleaned_data.get('use_file_subject', False)
            if not use_manual_subject or not email.subject:
                email.subject = subject_from_file

            use_manual_sender = form.cleaned_data.get('use_file_sender', False)
            if not use_manual_sender:
                if sender_from_file:
                    email.sender = sender_from_file
                else:
                    import re
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    email_matches = re.findall(email_pattern, content_from_file)
                    if email_matches:
                        email.sender = email_matches[0]
                    else:
                        email.sender = 'noreply@example.com'
            email.content = content_from_file

        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {str(e)}")
            if is_api:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao processar o arquivo: {str(e)}'
                }, status=400)
            raise e

    # Preparar dados do email para processamento
    email_data = {
        'subject': email.subject,
        'content': email.content,
        'sender': email.sender
    }

    # Salvar email com status temporário
    email.category = "pending"  # Status temporário até que o job seja concluído
    email.confidence_score = 0.0
    email.suggested_response = "Processando..."
    email.save()

    # Enfileirar para processamento completo com referência ao email
    job_id = queue_complete_email_processing(email_data, email.pk)

    # Retornar resposta ao cliente
    if is_api:
        queue_status = job_queue.get_queue_status()

        return JsonResponse({
            'status': 'queued',
            'message': 'Email submetido para processamento',
            'id': email.pk,
            'job_id': job_id,
            'queue_position': queue_status['queue_length'],
            'estimated_wait': queue_status['estimated_wait'],
            'queue_status': queue_status
        })

    return email

def api_email_detail(request, pk):
    """
    API para obter detalhes de um email específico.
    """
    try:
        email = get_object_or_404(Email, pk=pk)

        # Formatando a data para facilitar o processamento no frontend
        created_at_str = email.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            'id': email.id,
            'subject': email.subject,
            'content': email.content,
            'sender': email.sender,
            'category': email.category,
            'suggested_response': email.suggested_response,
            'created_at': created_at_str,
            'confidence_score': email.confidence_score
        }

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    except Exception as e:
        logger.error(f"Erro ao obter detalhes do email: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def api_emails_list(request):
    """
    API para listar todos os emails.
    """
    try:
        emails = Email.objects.all().order_by('-created_at')
        data = []

        for email in emails:
            created_at_str = email.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            data.append({
                'id': email.id,
                'subject': email.subject,
                'sender': email.sender,
                'category': email.category,
                'created_at': created_at_str,
                'confidence_score': email.confidence_score
            })

        response = JsonResponse(data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    except Exception as e:
        logger.error(f"Erro ao listar emails: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def api_job_status(request, job_id):
    """
    API para verificar o status de um job específico.
    """
    try:
        job = job_queue.get_job(job_id)

        if not job:
            return JsonResponse({
                'status': 'error',
                'message': f'Job não encontrado: {job_id}'
            }, status=404)

        job_data = job.to_dict()

        # Adicionar informações do email se for um job de processamento completo
        if job.job_type == "process_email_complete" and job.status == JobStatus.COMPLETED:
            email_id = job.data.get('email_id')
            if email_id:
                from .models import Email
                try:
                    email = Email.objects.get(pk=email_id)
                    job_data['email'] = {
                        'id': email.id,
                        'subject': email.subject,
                        'category': email.category,
                        'confidence_score': email.confidence_score,
                        'is_processed': email.category != 'pending'
                    }
                except Email.DoesNotExist:
                    job_data['email'] = {'error': 'Email não encontrado'}

        response = JsonResponse(job_data)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    except Exception as e:
        logger.error(f"Erro ao obter status do job: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
