from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0002_add_file_fields'),
        ('classifier', '0003_add_confidence_score'),
    ]

    operations = [
        # Esta migração não contém operações, apenas combina as duas migrações anteriores
    ]
