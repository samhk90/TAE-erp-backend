# Generated by Django 5.0.4 on 2024-08-11 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0015_attendance_classid'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='Subjectdep',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='erp_1.year'),
        ),
    ]
