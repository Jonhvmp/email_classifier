from django.db import models
import os
from django.utils.text import slugify

def get_upload_path(instance, filename):
    """Define o caminho para upload de arquivos de email"""
    from datetime import datetime
    ext = filename.split('.')[-1]
    subject_slug = slugify(instance.subject[:30])  # Limita o tamanho e normaliza o assunto
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f'uploads/{instance.sender.split("@")[0]}_{subject_slug}_{timestamp}.{ext}'

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
    confidence_score = models.FloatField(default=0.0, verbose_name='Nível de Confiança')
    # Made null=True to avoid migration issues
    classification_method = models.CharField(max_length=20, default='huggingface', blank=True,
                                           null=True, verbose_name='Método de Classificação')

    def __str__(self):
        return f"{self.subject} - {self.category}"

    @property
    def category_display(self):
        """Retorna o valor de exibição da categoria"""
        return dict(self._meta.get_field('category').choices).get(self.category, self.category)

    @property
    def is_productive(self):
        return self.category == 'productive'

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['sender']),
        ]
