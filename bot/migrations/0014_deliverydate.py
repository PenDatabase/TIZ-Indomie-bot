# Generated by Django 5.1.5 on 2025-01-24 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_alter_reciept_order_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
    ]
