# Generated by Django 4.2.6 on 2024-03-28 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_remove_album_imagen_album_artista_imagen_album'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artista',
            name='imagen_album',
            field=models.ImageField(null=True, upload_to='albums/'),
        ),
    ]
