# Generated by Django 5.1.3 on 2024-11-28 12:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("triptracker", "0006_alter_debt_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="tosettle",
            name="is_paid",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="debt",
            name="time",
            field=models.TimeField(default=datetime.time(18, 27, 37, 349178)),
        ),
    ]
