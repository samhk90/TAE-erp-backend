# Generated by Django 5.0.4 on 2024-08-12 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0023_subject_subjecttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='batch',
            field=models.IntegerField(default=1),
        ),
    ]