# Generated by Django 5.1.3 on 2024-11-17 13:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billsplit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together={('member', 'group')},
        ),
    ]
