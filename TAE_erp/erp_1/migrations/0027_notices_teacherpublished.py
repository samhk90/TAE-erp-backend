# Generated by Django 5.0.4 on 2024-08-26 05:09

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_1', '0026_remove_notices_teacherpublished'),
    ]

    operations = [
        migrations.AddField(
            model_name='notices',
            name='teacherpublished',
            field=models.ForeignKey(default=uuid.UUID('45d8c03d-0e93-48a7-b036-41ad381b7233'), on_delete=django.db.models.deletion.CASCADE, to='erp_1.teacher'),
        ),
    ]