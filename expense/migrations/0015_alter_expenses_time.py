# Generated by Django 5.1.3 on 2024-11-15 18:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0014_alter_expenses_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expenses",
            name="time",
            field=models.TimeField(default=datetime.time(23, 31, 27, 71331)),
        ),
    ]
