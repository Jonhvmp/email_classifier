from django.http import JsonResponse

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = JsonResponse({})
            # Adicionar cabeçalhos CORS para preflights
            response["Access-Control-Allow-Origin"] = "*"  # Para desenvolvimento local
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
            response["Access-Control-Allow-Headers"] = "*"
            response["Access-Control-Max-Age"] = "86400"  # 24 horas
            return response

        # Adicionar as origens confiáveis para CSRF
        if 'HTTP_ORIGIN' in request.META:
            origin = request.META['HTTP_ORIGIN']
            print(f"Origem detectada: {origin}")

        response = self.get_response(request)

        # Configurar cabeçalhos CORS para todas as respostas
        response["Access-Control-Allow-Origin"] = "*"  # Para desenvolvimento
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
        response["Access-Control-Allow-Headers"] = "*"

        return response
