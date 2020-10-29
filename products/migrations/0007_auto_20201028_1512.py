# Generated by Django 3.1.2 on 2020-10-28 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_inventory_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='inventory_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='variation_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
