# Generated by Django 5.0.1 on 2024-03-03 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0007_student_batch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='Batch',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
