# Generated by Django 5.1.3 on 2024-11-27 08:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('triptracker', '0005_alter_debt_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='time',
            field=models.TimeField(default=datetime.time(14, 5, 34, 335016)),
        ),
    ]
