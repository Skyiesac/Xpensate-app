# Generated by Django 5.1.3 on 2024-11-13 19:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0010_alter_expenses_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expenses",
            name="time",
            field=models.TimeField(default=datetime.time(0, 37, 55, 74287)),
        ),
    ]
