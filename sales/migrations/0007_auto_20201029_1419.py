# Generated by Django 3.1.2 on 2020-10-29 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_auto_20201029_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='date_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
