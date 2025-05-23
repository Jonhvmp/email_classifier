from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0002_add_file_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='confidence_score',
            field=models.FloatField(default=0.0, verbose_name='Nível de Confiança'),
        ),
    ]
