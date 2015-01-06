# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_activity_and_activitystat_tweaks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Activity',
            new_name='ActivityTrack',
        ),
    ]
