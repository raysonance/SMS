# Generated by Django 3.0.11 on 2020-12-04 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0007_auto_20201127_1219'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ['joining_date', 'full_name']},
        ),
        migrations.RenameField(
            model_name='teacher',
            old_name='name',
            new_name='full_name',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='created_by',
        ),
    ]