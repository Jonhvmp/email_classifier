from django.db import migrations, models
import os
from classifier.models import get_upload_path

class Migration(migrations.Migration):

    dependencies = [
        ('classifier', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=get_upload_path, verbose_name='Arquivo'),
        ),
        migrations.AddField(
            model_name='email',
            name='file_type',
            field=models.CharField(blank=True, max_length=10, verbose_name='Tipo de Arquivo'),
        ),
    ]
