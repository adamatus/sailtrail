# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    atomic = False

    database_operations = [
        migrations.AlterModelTable('Activity', 'api_activity'),
        migrations.AlterModelTable('ActivityTrack', 'api_activitytrack'),
        migrations.AlterModelTable('ActivityTrackpoint',
                                   'api_activitytrackpoint'),
    ]

    state_operations = [
        migrations.DeleteModel('Activity'),
        migrations.DeleteModel('ActivityTrack'),
        migrations.DeleteModel('ActivityTrackpoint'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
