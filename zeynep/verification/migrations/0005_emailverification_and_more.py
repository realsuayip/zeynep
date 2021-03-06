# Generated by Django 4.0.1 on 2022-02-08 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import zeynep.verification.models.base


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('verification', '0004_remove_registrationverification_unique_email_and_code_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('code', models.CharField(max_length=6, validators=[zeynep.verification.models.base.code_validator], verbose_name='code')),
                ('date_verified', models.DateTimeField(blank=True, null=True, verbose_name='date verified')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'email verification',
                'verbose_name_plural': 'email verifications',
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='emailverification',
            constraint=models.UniqueConstraint(fields=('email', 'code'), name='emailverification_unique_email_and_code'),
        ),
    ]
