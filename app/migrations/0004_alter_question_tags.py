# Generated by Django 5.2 on 2025-04-08 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_question_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='questions', to='app.tag'),
        ),
    ]
