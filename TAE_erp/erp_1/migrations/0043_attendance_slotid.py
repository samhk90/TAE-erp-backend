# Generated by Django 5.0.4 on 2024-10-29 05:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0042_timetable_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='SlotID',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='erp_1.slots'),
        ),
    ]
