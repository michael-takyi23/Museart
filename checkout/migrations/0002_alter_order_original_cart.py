# Generated by Django 5.1 on 2025-03-09 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="original_cart",
            field=models.TextField(default="{}"),
        ),
    ]
