from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('classifier', '0006_email_classifier__categor_a8a30b_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='user_ip',
            field=models.GenericIPAddressField(null=True, blank=True, verbose_name='IP do Usuário'),
        ),
        migrations.AddIndex(
            model_name='email',
            index=models.Index(fields=['user_ip'], name='classifier__user_ip_idx'),
        ),
    ]
