# Generated by Django 3.0.11 on 2021-04-23 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_subjectresult_sub_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectresult',
            name='head_teacher_comment',
            field=models.CharField(max_length=100, null=True),
        ),
    ]