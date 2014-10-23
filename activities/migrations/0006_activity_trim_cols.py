# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0005_activitystat_max_speed_to_float'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='trim_end',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='trim_start',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
