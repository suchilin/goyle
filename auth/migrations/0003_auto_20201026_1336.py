# Generated by Django 3.1.2 on 2020-10-26 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_mlstate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlstate',
            name='token',
            field=models.CharField(default='5525206618c465443217b1b63de1705ffb3696e433bcff0de30451b6c82416bc', max_length=255),
        ),
    ]
