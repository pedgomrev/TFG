# Generated by Django 4.2.6 on 2024-04-07 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_remove_usuario_follow_remove_usuario_follower_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='follower', to='main.usuario'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='follows',
            field=models.ManyToManyField(blank=True, related_name='follow', to='main.usuario'),
        ),
    ]
