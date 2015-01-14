# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_add_master_activity_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitytrack',
            name='activity_id',
            field=models.ForeignKey(to='activities.Activity', related_name='track'),
            preserve_default=True,
        ),
    ]
