# Generated by Django 5.1.1 on 2024-09-13 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_customuser_current_device_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='current_device_token',
        ),
    ]
