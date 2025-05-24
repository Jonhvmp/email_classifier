from django.db import migrations, models

def populate_user_ip(apps, schema_editor):
    """Popula o campo user_ip para emails existentes"""
    Email = apps.get_model('classifier', 'Email')
    # Para emails existentes sem user_ip, definir um IP padrão
    # Isso permite que sejam visualizados até que novos emails sejam criados
    Email.objects.filter(user_ip__isnull=True).update(user_ip='127.0.0.1')

def reverse_populate_user_ip(apps, schema_editor):
    """Reverter a população do user_ip"""
    Email = apps.get_model('classifier', 'Email')
    Email.objects.filter(user_ip='127.0.0.1').update(user_ip=None)

class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0006_email_classifier__categor_a8a30b_idx_and_more'),
    ]

    operations = [
        # Garantir que o campo user_ip existe e não é nulo
        migrations.AlterField(
            model_name='email',
            name='user_ip',
            field=models.GenericIPAddressField(default='127.0.0.1', verbose_name='IP do Usuário'),
        ),
        # Preencher emails existentes com IP padrão
        migrations.RunPython(populate_user_ip, reverse_populate_user_ip),
    ]
