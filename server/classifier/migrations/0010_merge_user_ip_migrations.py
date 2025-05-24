from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0008_fix_user_ip_field'),
    ]

    operations = [
        # Esta migração resolve o conflito removendo a dependência da 0009
        # que foi removida por ser redundante
    ]
