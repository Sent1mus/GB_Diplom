# Generated by Django 5.0.4 on 2024-05-05 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_alter_administrator_phone_alter_customer_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrator',
            name='phone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='phone',
            field=models.CharField(max_length=20),
        ),
    ]
