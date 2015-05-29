# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0021_activity_remove_stats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitydetail',
            name='activity_id',
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.CharField(max_length=2, choices=[('SL', 'Sailing'), ('WS', 'Windsurfing'), ('KB', 'Kite Boarding'), ('SK', 'Snow Kiting'), ('IB', 'Ice Boating')], default='SL'),
        ),
        migrations.AddField(
            model_name='activity',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='private',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='ActivityDetail',
        ),
    ]
