# Generated by Django 5.1.5 on 2025-01-22 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_reciept'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='user_id',
            field=models.BigIntegerField(),
        ),
    ]
