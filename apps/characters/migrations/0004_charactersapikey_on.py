# Generated by Django 4.2 on 2024-07-05 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0003_character_is_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='charactersapikey',
            name='on',
            field=models.BooleanField(default=True, verbose_name='Включен'),
        ),
    ]
