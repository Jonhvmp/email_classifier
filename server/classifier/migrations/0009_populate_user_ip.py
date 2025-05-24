from django.db import migrations

def populate_user_ip(apps, schema_editor):
    """Popula o campo user_ip para emails existentes"""
    Email = apps.get_model('classifier', 'Email')
    # Para emails existentes sem user_ip, definir um IP padrão
    # Isso permite que sejam visualizados até que novos emails sejam criados
    emails_updated = Email.objects.filter(user_ip__isnull=True).update(user_ip='127.0.0.1')
    print(f"Atualizados {emails_updated} emails com IP padrão")

def reverse_populate_user_ip(apps, schema_editor):
    """Reverter a população do user_ip"""
    Email = apps.get_model('classifier', 'Email')
    Email.objects.filter(user_ip='127.0.0.1').update(user_ip=None)

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0007_add_user_ip_field'),
    ]

    operations = [
        # Preencher emails existentes com IP padrão
        migrations.RunPython(populate_user_ip, reverse_populate_user_ip),
    ]
