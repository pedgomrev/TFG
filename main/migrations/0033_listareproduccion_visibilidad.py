# Generated by Django 4.2.6 on 2024-05-09 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_publicacion_like_comentario'),
    ]

    operations = [
        migrations.AddField(
            model_name='listareproduccion',
            name='visibilidad',
            field=models.BooleanField(default=True),
        ),
    ]
