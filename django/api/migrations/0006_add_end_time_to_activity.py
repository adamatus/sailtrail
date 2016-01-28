# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160118_1943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-start']},
        ),
        migrations.RenameField(
            model_name='activity',
            old_name='datetime',
            new_name='start',
        ),
        migrations.AddField(
            model_name='activity',
            name='end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='activitytrack',
            name='activity',
            field=models.ForeignKey(related_name='tracks', to='api.Activity'),
        ),
        migrations.AlterField(
            model_name='activitytrackpoint',
            name='track',
            field=models.ForeignKey(related_name='trackpoints', to='api.ActivityTrack'),
        ),
    ]
