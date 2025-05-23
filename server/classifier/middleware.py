from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log da requisição para debug
        origin = request.META.get('HTTP_ORIGIN', 'N/A')
        logger.info(f"Requisição recebida: {request.method} {request.path} Origin: {origin}")

        # Lista de origens permitidas
        allowed_origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'https://email-classifier-ten.vercel.app',
            'https://email-classifier-ten.vercel.app/',
        ]

        # Verificar se a origem está na lista ou é do Vercel
        origin_allowed = (
            origin in allowed_origins or
            (origin and '.vercel.app' in origin) or
            origin == 'null'  # Para testes locais
        )

        # Definir origem para cabeçalhos CORS
        cors_origin = origin if origin_allowed else '*'

        if request.method == "OPTIONS":
            logger.info(f"Requisição OPTIONS de origem: {origin}")
            response = JsonResponse({})
            response["Access-Control-Allow-Origin"] = cors_origin
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"  # 24 horas
            return response

        # Processar requisição normal
        try:
            response = self.get_response(request)
            logger.info(f"Response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            response = JsonResponse({
                'status': 'error',
                'message': 'Erro interno do servidor'
            }, status=500)

        # Configurar cabeçalhos CORS para todas as respostas
        response["Access-Control-Allow-Origin"] = cors_origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"

        return response
