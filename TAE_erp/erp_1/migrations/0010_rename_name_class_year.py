# Generated by Django 5.0.1 on 2024-03-04 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0009_subject_subjectbatch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='class',
            old_name='name',
            new_name='year',
        ),
    ]
