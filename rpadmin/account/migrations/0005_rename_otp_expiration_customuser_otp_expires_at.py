# Generated by Django 5.1.1 on 2024-09-13 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_customuser_otp_customuser_otp_expiration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='otp_expiration',
            new_name='otp_expires_at',
        ),
    ]