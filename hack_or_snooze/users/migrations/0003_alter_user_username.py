# Generated by Django 5.0 on 2024-01-01 15:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='Only alphanumeric characters are allowed.', regex='^[0-9a-zA-Z]*$')]),
        ),
    ]
