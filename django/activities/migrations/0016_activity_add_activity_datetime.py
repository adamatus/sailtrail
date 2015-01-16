# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0015_activitydetail_add_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['datetime']},
        ),
        migrations.AddField(
            model_name='activity',
            name='datetime',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
