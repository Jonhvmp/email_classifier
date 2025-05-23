import os

# Cria os diretórios necessários se não existirem
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
UPLOADS_DIR = os.path.join(MEDIA_ROOT, 'uploads')

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
