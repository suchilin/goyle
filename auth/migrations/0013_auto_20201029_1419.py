# Generated by Django 3.1.2 on 2020-10-29 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_auto_20201029_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlstate',
            name='token',
            field=models.CharField(default='630de3045d9a12005bc122e85defd06424386ddafe478551fbf26862a4e8a755', max_length=255),
        ),
    ]
