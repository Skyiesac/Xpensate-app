# Generated by Django 5.1.2 on 2024-11-10 14:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0003_expenses_is_credit_alter_expenses_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='time',
            field=models.TimeField(default=datetime.time(19, 36, 41, 419659)),
        ),
    ]