from django.db import models
import os

def get_upload_path(instance, filename):
    """Define o caminho para upload de arquivos de email"""
    ext = filename.split('.')[-1]
    return f'uploads/{instance.sender}_{instance.subject}_{instance.created_at.strftime("%Y%m%d%H%M%S")}.{ext}'

class Email(models.Model):
    subject = models.CharField(max_length=200, verbose_name='Assunto')
    content = models.TextField(verbose_name='Conteúdo')
    sender = models.EmailField(verbose_name='Remetente')
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True, verbose_name='Arquivo')
    file_type = models.CharField(max_length=10, blank=True, verbose_name='Tipo de Arquivo')
    category = models.CharField(max_length=20, choices=[
        ('productive', 'Produtivo'),
        ('unproductive', 'Improdutivo'),
    ], blank=True, verbose_name='Categoria')
    suggested_response = models.TextField(blank=True, verbose_name='Resposta Sugerida')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    def __str__(self):
        return f"{self.subject} - {self.category}"

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        ordering = ['-created_at']
