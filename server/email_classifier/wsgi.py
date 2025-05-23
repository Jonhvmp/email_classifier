"""
WSGI config for email_classifier project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, '/app')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_classifier.settings')

try:
    logger.info("Inicializando aplicação WSGI...")

    # Verificar se Django consegue inicializar
    import django
    django.setup()
    logger.info("Django setup concluído")

    # Criar aplicação WSGI
    application = get_wsgi_application()
    logger.info("Aplicação WSGI inicializada com sucesso")

    # Teste rápido da aplicação
    from django.test import RequestFactory
    from django.urls import reverse

    factory = RequestFactory()
    request = factory.get('/api/status/')

    # Não podemos testar aqui pois vai criar loop infinito
    logger.info("WSGI application pronta para servir requisições")

except Exception as e:
    logger.error(f"Erro ao inicializar aplicação WSGI: {e}")
    logger.error(f"Caminho Python: {sys.path}")
    logger.error(f"Diretório atual: {os.getcwd()}")
    raise
