# Generated by Django 5.1.3 on 2024-11-20 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0007_remove_user_appassword_user_currency_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='income',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
