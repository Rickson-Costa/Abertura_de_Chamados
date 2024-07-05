# Generated by Django 5.0.6 on 2024-07-05 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_timeline_resposta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arquivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to='timelines/')),
                ('descricao', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='timeline',
            name='arquivos',
            field=models.ManyToManyField(blank=True, related_name='timelines', to='main.arquivo'),
        ),
    ]