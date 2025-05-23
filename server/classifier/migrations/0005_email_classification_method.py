from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0004_merge_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='classification_method',
            field=models.CharField(blank=True, default='huggingface', max_length=20, null=True, verbose_name='Método de Classificação'),
        ),
    ]
