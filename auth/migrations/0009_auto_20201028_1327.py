# Generated by Django 3.1.2 on 2020-10-28 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20201028_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlstate',
            name='token',
            field=models.CharField(default='32c91832fad1852b9bc9366742f751abac49213d76312cef95fe8c6b06202a82', max_length=255),
        ),
    ]
