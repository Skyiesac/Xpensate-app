# Generated by Django 5.1.3 on 2024-11-24 07:09

import datetime
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("triptracker", "0003_alter_tosettle_group"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Debt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("1.00"))
                        ],
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=255)),
                ("date", models.DateField(default=datetime.date.today)),
                ("time", models.TimeField(default=datetime.time(12, 39, 3, 943282))),
                ("lend", models.BooleanField(default=False)),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
