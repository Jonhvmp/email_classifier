#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run administrative tasks."""
    # Configurar variáveis de ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_classifier.settings')

    # Log do ambiente atual
    logger.info(f"Iniciando Django management command: {' '.join(sys.argv)}")
    logger.info(f"Diretório atual: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:3]}")  # Primeiros 3 para brevidade
    logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

    # Verificar se estamos no Railway
    if any(key in os.environ for key in ['RAILWAY_ENVIRONMENT', 'DATABASE_URL', 'RAILWAY_STATIC_URL']):
        logger.info("Ambiente Railway detectado")
        # Adicionar diretório atual ao Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            logger.info(f"Adicionado ao Python path: {current_dir}")

    try:
        from django.core.management import execute_from_command_line
        logger.info("Django management importado com sucesso")
    except ImportError as exc:
        logger.error(f"Erro ao importar Django: {exc}")
        logger.error(f"Python path atual: {sys.path}")
        logger.error(f"Diretório de trabalho: {os.getcwd()}")
        logger.error(f"Arquivos no diretório atual: {os.listdir('.')}")

        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        logger.info(f"Executando comando: {' '.join(sys.argv)}")
        execute_from_command_line(sys.argv)
        logger.info("Comando Django executado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao executar comando Django: {e}")
        raise

if __name__ == '__main__':
    main()
