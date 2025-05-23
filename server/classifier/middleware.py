from django.http import JsonResponse, HttpResponse
import logging
import os

logger = logging.getLogger(__name__)

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Lista de origens permitidas
        self.allowed_origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'https://email-classifier-ten.vercel.app',
        ]

        # Adicionar quaisquer origens adicionais da variável de ambiente
        if os.environ.get('CORS_ORIGIN_WHITELIST'):
            extra_origins = os.environ['CORS_ORIGIN_WHITELIST'].split(',')
            self.allowed_origins.extend(extra_origins)
            logger.info(f"Adicionadas origens CORS da variavel de ambiente: {extra_origins}")

        # Remover duplicatas
        self.allowed_origins = list(set(self.allowed_origins))
        logger.info(f"CORS middleware iniciado. Origens permitidas: {self.allowed_origins}")

    def __call__(self, request):
        # Log detalhado da requisição
        origin = request.META.get('HTTP_ORIGIN', 'N/A')
        method = request.method
        path = request.path
        user_agent = request.META.get('HTTP_USER_AGENT', 'N/A')[:50]

        logger.info(f"CORS: {method} {path} | Origin: {origin} | UA: {user_agent}")

        # Permitir todas as origens se configurado
        allow_all = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 't')

        # Verificar se a origem está na lista ou é do Vercel
        origin_allowed = (
            allow_all or
            origin in self.allowed_origins or
            (origin and '.vercel.app' in origin) or
            origin == 'null'  # Para testes locais
        )

        logger.info(f"CORS: Origin permitida: {origin_allowed} (allow_all: {allow_all})")

        # Tratar requisições OPTIONS (preflight)
        if method == "OPTIONS":
            logger.info(f"CORS: Tratando requisicao OPTIONS/preflight de origem: {origin}")

            response = HttpResponse()
            response.status_code = 200

            # Definir origem para cabeçalhos CORS
            if origin_allowed:
                response["Access-Control-Allow-Origin"] = origin if origin != 'N/A' else '*'
            else:
                response["Access-Control-Allow-Origin"] = '*'

            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin, Cache-Control, Pragma"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"

            # Headers adicionais para debug
            response["X-CORS-Debug"] = f"Origin: {origin}, Allowed: {origin_allowed}"

            logger.info(f"CORS: Resposta OPTIONS enviada com headers CORS")
            return response

        # Processar requisição normal
        try:
            response = self.get_response(request)
            logger.info(f"CORS: Response status: {response.status_code} para {method} {path}")
        except Exception as e:
            logger.error(f"CORS: Erro ao processar requisicao: {e}")
            response = JsonResponse({
                'status': 'error',
                'message': f'Erro interno do servidor: {str(e)}'
            }, status=500)

        # Configurar cabeçalhos CORS para todas as respostas
        if origin_allowed:
            response["Access-Control-Allow-Origin"] = origin if origin != 'N/A' else '*'
        else:
            response["Access-Control-Allow-Origin"] = '*'

        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin, Cache-Control, Pragma"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"

        # Headers adicionais de segurança
        response["X-Content-Type-Options"] = "nosniff"
        response["X-CORS-Debug"] = f"Origin: {origin}, Method: {method}, Status: {response.status_code}"

        logger.info(f"CORS: Headers adicionados à resposta")
        return response
