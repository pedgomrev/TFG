# Generated by Django 4.2.6 on 2024-03-12 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_cancion_duracion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cancion',
            name='duracion',
            field=models.IntegerField(),
        ),
    ]
