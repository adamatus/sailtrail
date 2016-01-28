# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_add_end_time_to_activity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activity',
            old_name='model_distance',
            new_name='distance',
        ),
        migrations.RenameField(
            model_name='activity',
            old_name='model_max_speed',
            new_name='max_speed',
        ),
    ]
