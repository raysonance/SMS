# Generated by Django 3.0.11 on 2021-05-23 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_auto_20210518_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmodel',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]