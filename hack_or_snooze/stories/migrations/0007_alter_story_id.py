# Generated by Django 5.0 on 2024-01-15 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0006_alter_story_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='id',
            field=models.CharField(default='57311364-e99c-4945-9f56-c511e32ec325', primary_key=True, serialize=False),
        ),
    ]