# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0018_activity_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitydetail',
            name='private',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
