# Generated by Django 5.1.2 on 2024-10-29 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Authentication", "0003_register_user_confirm_password_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailotp",
            name="forgot",
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
