# Generated by Django 3.0.11 on 2021-02-04 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210123_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminmodel',
            name='address',
            field=models.TextField(default='reddit'),
        ),
    ]