# Generated by Django 4.0.1 on 2022-01-15 12:10

from django.db import migrations
import zeynep.auth.models.managers


class Migration(migrations.Migration):

    dependencies = [
        ('zeynep_auth', '0002_user_display_name'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', zeynep.auth.models.managers.UserManager()),
            ],
        ),
    ]
