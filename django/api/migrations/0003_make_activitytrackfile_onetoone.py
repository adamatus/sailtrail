# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_activitytrackfile_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitytrackfile',
            name='track',
            field=models.OneToOneField(to='api.ActivityTrack', related_name='original_file', on_delete=models.CASCADE),
        ),
    ]
