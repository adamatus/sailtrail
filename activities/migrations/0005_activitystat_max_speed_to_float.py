# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0004_activitystat_add_max_speed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitystat',
            name='model_max_speed',
            field=models.FloatField(null=True),
        ),
    ]
