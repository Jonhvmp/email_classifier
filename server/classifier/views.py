from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
import logging
import sys
import os
from datetime import datetime
from django.conf import settings
import django
from .models import Email
from .forms import EmailForm
from .utils import extract_text_from_file
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_service import process_email, queue_email_processing, queue_complete_email_processing, gemini_limiter, job_queue
from .job_queue import JobStatus

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Obtém o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    """
    View da página inicial com formulário para submissão de email.
    """
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HTTP_ORIGIN' in request.META

        form = EmailForm(request.POST, request.FILES)
        logger.info(f"Processando formulário, é válido? {form.is_valid()}")

        if form.is_valid():
            # Obter IP do usuário
            user_ip = get_client_ip(request)
            logger.info(f"Processando email de IP: {user_ip}")

            email = form.save(commit=False)
            email.user_ip = user_ip  # Salvar IP do usuário
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
                logger.info(f"Email salvo com ID: {email.pk} para IP: {user_ip}")

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
    View para listar emails classificados - APENAS DO USUÁRIO ATUAL.
    """
    model = Email
    template_name = 'classifier/email_list.html'
    context_object_name = 'emails'
    paginate_by = 10

    def get_queryset(self):
        """Filtra emails apenas do IP do usuário atual"""
        user_ip = get_client_ip(self.request)
        logger.info(f"Listando emails para IP: {user_ip}")
        return Email.objects.filter(user_ip=user_ip).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_ip = get_client_ip(self.request)
        context['user_ip'] = user_ip
        context['total_emails'] = Email.objects.filter(user_ip=user_ip).count()
        return context

class EmailDetailView(DetailView):
    """
    View para mostrar os detalhes de um email específico - APENAS SE FOR DO USUÁRIO.
    """
    model = Email
    template_name = 'classifier/email_detail.html'
    context_object_name = 'email'

    def get_queryset(self):
        """Só permite acesso a emails do próprio IP"""
        user_ip = get_client_ip(self.request)
        return Email.objects.filter(user_ip=user_ip)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_ip'] = get_client_ip(self.request)
        return context

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
        # Log importante para debug
        origin = request.headers.get('origin', request.META.get('HTTP_ORIGIN', 'desconhecida'))
        method = request.method
        logger.info(f"API status chamado: {method} {request.path} - Origem: {origin}")

        # Tratar OPTIONS explicitamente se necessário
        if method == "OPTIONS":
            logger.info("API status: Tratando requisicao OPTIONS")
            response = JsonResponse({'status': 'options_ok'})
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

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

        # Verificar conexão com banco de dados
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            db_status = "connected"
            db_engine = connection.vendor
            logger.info("Conexão com banco de dados OK")
        except Exception as e:
            db_status = f"error: {str(e)}"
            db_engine = "unknown"
            logger.error(f"Erro de conexão com banco: {e}")

        # Verificar sistema operacional
        import platform
        os_info = f"{platform.system()} {platform.version()}"

        # Verificar status do job queue
        queue_status = "available"
        try:
            from .job_queue import job_queue
            queue_info = job_queue.get_queue_status()
            queue_length = queue_info['queue_length']
            queue_status = f"ok ({queue_length} job(s) na fila)"
            logger.info(f"Job queue OK: {queue_length} jobs")
        except Exception as e:
            queue_status = f"error: {str(e)}"
            logger.error(f"Erro ao obter status da fila de jobs: {e}")

        # Preparar dados de resposta
        response_data = {
            "status": "online",
            "message": "API está funcionando corretamente",
            "version": "1.0.7",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "python_version": sys.version,
                "django_version": django.get_version(),
                "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
                "port": os.environ.get('PORT', '8000'),
                "workers": os.environ.get('WEB_CONCURRENCY', '1'),
                "working_directory": os.getcwd(),
                "python_path": sys.path[:3]  # Primeiros 3 paths para debug
            },
            "database": {
                "status": db_status,
                "engine": db_engine
            },
            "job_queue": queue_status,
            "system": os_info,
            "endpoints": endpoints,
            "debug_mode": settings.DEBUG,
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "cors_origins": getattr(settings, 'CORS_ALLOWED_ORIGINS', "all"),
            "request": {
                "path": request.path,
                "method": request.method,
                "origin": origin,
                "remote_addr": request.META.get('REMOTE_ADDR', 'unknown'),
                "user_agent": request.META.get('HTTP_USER_AGENT', 'unknown')[:100]
            }
        }

        # Criar resposta JSON
        response = JsonResponse(response_data)

        # Garantir headers CORS explicitamente
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"
        response["X-API-Version"] = "1.0.7"

        logger.info("API status response enviada com sucesso")
        return response

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erro no endpoint api_status: {e}")
        logger.error(f"Traceback completo: {error_trace}")

        response = JsonResponse({
            "status": "error",
            "message": f"Erro interno: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "traceback": error_trace.split('\n')[-10:]  # Últimas 10 linhas do traceback
        }, status=500)

        # Garantir headers CORS mesmo em caso de erro
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin"
        response["Access-Control-Allow-Credentials"] = "true"

        return response

def _add_cors_headers(response, origin=None):
    """Adiciona cabeçalhos CORS a uma resposta"""
    # Lista de origens permitidas
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://email-classifier-ten.vercel.app',
    ]

    # Verificar se a origem é permitida
    if origin and (origin in allowed_origins or '.vercel.app' in origin):
        response["Access-Control-Allow-Origin"] = origin
    else:
        response["Access-Control-Allow-Origin"] = "*"

    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken"
    response["Access-Control-Allow-Credentials"] = "true"

def api_usage(request):
    """
    API para obter estatísticas de uso da API.
    """
    try:
        # Log da origem da requisição
        origin = request.headers.get('origin', request.META.get('HTTP_ORIGIN', 'desconhecida'))
        logger.info(f"API usage chamado, origem: {origin}")

        # Obter estatísticas dos rate limiters
        try:
            from .ai_service import gemini_limiter
            gemini_stats = gemini_limiter.get_stats()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do Gemini: {e}")
            gemini_stats = {
                "minute_usage": 0,
                "minute_limit": 0,
                "minute_percent": 0,
                "day_usage": 0,
                "day_limit": 0,
                "day_percent": 0,
                "total_today": 0,
                "error": str(e)
            }

        # Obter estatísticas da fila de jobs
        try:
            from .job_queue import job_queue
            queue_stats = job_queue.get_queue_status()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da fila: {e}")
            queue_stats = {
                "queue_length": 0,
                "active_job": None,
                "estimated_wait": 0,
                "queued_jobs": [],
                "processing_count": 0,
                "error": str(e)
            }

        data = {
            "gemini_api": gemini_stats,
            "job_queue": queue_stats,
            "timestamp": datetime.now().isoformat(),
            "server_version": "1.0.6",
            "status": "operational",
            "request": {
                "path": request.path,
                "method": request.method,
                "origin": origin
            }
        }

        response = JsonResponse(data)
        logger.info("✅ API usage response enviada com sucesso")
        return response

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de uso: {str(e)}")
        response = JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=500)
        return response

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
        # Obter IP do usuário para API
        user_ip = get_client_ip(request)
        logger.info(f"API submit email de IP: {user_ip}")

        form = EmailForm(request.POST, request.FILES)

        if not form.is_valid():
            logger.error(f"Form inválido: {form.errors}")
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.as_json()
            }, status=400)

        # Usar versão assíncrona com IP
        return _process_valid_form_async(form, is_api=True, user_ip=user_ip)

    except Exception as e:
        logger.error(f"ERRO geral: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }, status=500)

def _process_valid_form_async(form, is_api=False, user_ip=None):
    """
    Processa um formulário válido de forma assíncrona usando a fila.
    """
    email = form.save(commit=False)

    # Definir IP do usuário se não fornecido
    if user_ip:
        email.user_ip = user_ip

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

def api_emails_list(request):
    """
    API para listar emails - APENAS DO USUÁRIO ATUAL.
    """
    try:
        user_ip = get_client_ip(request)
        emails = Email.objects.filter(user_ip=user_ip).order_by('-created_at')

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

        response = JsonResponse({
            'emails': data,
            'count': len(data),
            'user_ip': user_ip  # Para debug
        })
        _add_cors_headers(response, request.headers.get('origin'))
        return response

    except Exception as e:
        logger.error(f"Erro ao listar emails: {str(e)}")
        response = JsonResponse({"error": str(e)}, status=500)
        _add_cors_headers(response, request.headers.get('origin'))
        return response

def api_email_detail(request, pk):
    """
    API para obter detalhes de um email específico - APENAS SE FOR DO USUÁRIO.
    """
    try:
        user_ip = get_client_ip(request)
        email = get_object_or_404(Email, pk=pk, user_ip=user_ip)

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
        _add_cors_headers(response, request.headers.get('origin'))
        return response

    except Exception as e:
        logger.error(f"Erro ao obter detalhes do email: {str(e)}")
        response = JsonResponse({"error": str(e)}, status=500)
        _add_cors_headers(response, request.headers.get('origin'))
        return response

def api_job_status(request, job_id):
    """
    API para verificar o status de um job específico na fila.
    """
    try:
        origin = request.headers.get('origin', 'desconhecida')
        logger.info(f"API job status chamado para job {job_id}, origem: {origin}")

        # Obter o job da fila
        job = job_queue.get_job(job_id)

        if not job:
            return JsonResponse({
                'status': 'error',
                'message': f'Job {job_id} não encontrado'
            }, status=404)

        # Retornar dados do job
        job_data = job.to_dict()

        # Se o job foi concluído e tem resultado, incluir detalhes do email
        if job.status == JobStatus.COMPLETED and job.result:
            # Verificar se o resultado contém dados de email processado
            if isinstance(job.result, dict) and 'email_id' in job.data:
                try:
                    user_ip = get_client_ip(request)
                    email = Email.objects.filter(pk=job.data['email_id'], user_ip=user_ip).first()

                    if email:
                        job_data['email'] = {
                            'id': email.id,
                            'subject': email.subject,
                            'category': email.category,
                            'confidence_score': email.confidence_score,
                            'is_processed': email.category not in ['pending', 'error']
                        }
                except Exception as e:
                    logger.error(f"Erro ao obter dados do email para job {job_id}: {e}")

        response = JsonResponse(job_data)
        _add_cors_headers(response, request.headers.get('origin'))
        return response

    except Exception as e:
        logger.error(f"Erro ao obter status do job {job_id}: {str(e)}")
        response = JsonResponse({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }, status=500)
        _add_cors_headers(response, request.headers.get('origin'))
        return response
