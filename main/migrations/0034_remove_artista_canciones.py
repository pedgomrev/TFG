# Generated by Django 4.2.6 on 2024-05-15 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_listareproduccion_visibilidad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artista',
            name='canciones',
        ),
    ]
