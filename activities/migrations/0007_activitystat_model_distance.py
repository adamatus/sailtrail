# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0006_activity_trim_cols'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitystat',
            name='model_distance',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
    ]
