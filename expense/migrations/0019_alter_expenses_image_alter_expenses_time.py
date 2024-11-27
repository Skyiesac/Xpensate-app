# Generated by Django 5.1.3 on 2024-11-27 08:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0018_alter_expenses_time_budget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='upload_pics/'),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='time',
            field=models.TimeField(default=datetime.time(14, 5, 34, 331030)),
        ),
    ]
