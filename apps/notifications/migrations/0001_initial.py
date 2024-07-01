# Generated by Django 4.2 on 2024-07-01 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_emails', models.BooleanField(default=True, verbose_name='Отправка писем включена')),
            ],
            options={
                'verbose_name': 'Настройки email',
                'db_table': 'email_settings',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_type', models.CharField(choices=[('confirm_email', 'Подтверждение адреса электронной почты'), ('password_reset', 'Восстановление пароля')], max_length=64, unique=True, verbose_name='Тип письма')),
                ('subject', models.CharField(max_length=256, verbose_name='Тема')),
                ('message', models.TextField(verbose_name='Сообщение')),
            ],
            options={
                'verbose_name': 'Шаблон письма',
                'verbose_name_plural': 'Шаблоны писем',
                'db_table': 'email_templates',
            },
        ),
    ]