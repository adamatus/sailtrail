# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0010_activity_trimmed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-trim_start']},
        ),
        migrations.RemoveField(
            model_name='activitystat',
            name='datetime',
        ),
        migrations.RemoveField(
            model_name='activitystat',
            name='duration',
        ),
    ]
