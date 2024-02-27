# Generated by Django 5.0 on 2024-02-02 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0008_alter_story_id'),
        ('users', '0009_alter_user_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favorited_by', to='stories.story'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
    ]