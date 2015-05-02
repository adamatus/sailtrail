# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0019_activitydetail_private'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitytrack',
            name='upfile',
        ),
        migrations.AddField(
            model_name='activitytrack',
            name='original_filename',
            field=models.CharField(default='missing', max_length=255),
            preserve_default=False,
        ),
    ]
