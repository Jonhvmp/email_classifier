from django.http import JsonResponse
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
            logger.info(f"Adicionadas origens CORS da variável de ambiente: {extra_origins}")

        # Remover duplicatas
        self.allowed_origins = list(set(self.allowed_origins))
        logger.info(f"CORS middleware iniciado. Origens permitidas: {self.allowed_origins}")

    def __call__(self, request):
        # Log da requisição para debug
        origin = request.META.get('HTTP_ORIGIN', 'N/A')
        method = request.method
        path = request.path

        logger.info(f"Requisição recebida: {method} {path} Origin: {origin}")

        # Permitir todas as origens se configurado
        allow_all = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 't')

        # Verificar se a origem está na lista ou é do Vercel
        origin_allowed = (
            allow_all or
            origin in self.allowed_origins or
            (origin and '.vercel.app' in origin) or
            origin == 'null'  # Para testes locais
        )

        # Definir origem para cabeçalhos CORS
        cors_origin = origin if origin_allowed else '*'

        if method == "OPTIONS":
            logger.info(f"Requisição OPTIONS de origem: {origin}")
            response = JsonResponse({})
            self._add_cors_headers(response, cors_origin)
            return response

        # Processar requisição normal
        try:
            response = self.get_response(request)
            logger.info(f"Response status: {response.status_code} para {method} {path}")
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            response = JsonResponse({
                'status': 'error',
                'message': f'Erro interno do servidor: {str(e)}'
            }, status=500)

        # Configurar cabeçalhos CORS para todas as respostas
        self._add_cors_headers(response, cors_origin)
        return response

    def _add_cors_headers(self, response, origin):
        """Adiciona os cabeçalhos CORS adequados à resposta"""
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Accept, Authorization, X-CSRFToken, Origin"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"  # 24 horas

        # Adicionar outros cabeçalhos de segurança padrão
        response["X-Content-Type-Options"] = "nosniff"
        return response
