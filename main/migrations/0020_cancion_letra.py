# Generated by Django 4.2.6 on 2024-03-28 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_artista_imagen_album'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancion',
            name='letra',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
