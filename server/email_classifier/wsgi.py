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

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_classifier.settings')

try:
    logger.info("Inicializando aplicação WSGI...")
    application = get_wsgi_application()
    logger.info("✅ Aplicação WSGI inicializada com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar aplicação WSGI: {e}")
    raise
