# Generated by Django 5.1.3 on 2024-11-11 16:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0007_alter_expenses_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expenses",
            name="time",
            field=models.TimeField(default=datetime.time(21, 51, 15, 606125)),
        ),
    ]
