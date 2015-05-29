# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0020_activitytrack_no_more_filefield'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitystat',
            name='activity_id',
        ),
        migrations.AddField(
            model_name='activity',
            name='model_distance',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='model_max_speed',
            field=models.FloatField(null=True),
        ),
        migrations.DeleteModel(
            name='ActivityStat',
        ),
    ]
