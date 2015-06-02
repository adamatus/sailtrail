# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0022_activity_remove_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='wind_direction',
            field=models.FloatField(null=True),
        ),
    ]
