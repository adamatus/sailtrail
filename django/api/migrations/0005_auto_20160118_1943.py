# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160118_1935'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activitytrackpoint',
            old_name='track_id',
            new_name='track',
        ),
    ]
