# Generated by Django 4.2.6 on 2024-04-14 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_listareproduccion_foto_alter_album_foto_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='foto_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_perfil', verbose_name='Foto de Perfil'),
        ),
    ]