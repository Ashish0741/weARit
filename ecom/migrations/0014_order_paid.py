# Generated by Django 3.1.7 on 2021-10-01 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0013_auto_20211001_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
