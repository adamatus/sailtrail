# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0008_activitytrackpoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='trim_end',
            field=models.DateTimeField(null=True, default=None),
        ),
        migrations.AlterField(
            model_name='activity',
            name='trim_start',
            field=models.DateTimeField(null=True, default=None),
        ),
    ]
