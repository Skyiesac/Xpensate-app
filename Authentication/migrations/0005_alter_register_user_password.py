# Generated by Django 5.1.3 on 2024-11-12 11:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Authentication", "0004_emailotp_forgot"),
    ]

    operations = [
        migrations.AlterField(
            model_name="register_user",
            name="password",
            field=models.CharField(
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(
                        8, "Password must have 8 letters"
                    )
                ],
            ),
        ),
    ]
