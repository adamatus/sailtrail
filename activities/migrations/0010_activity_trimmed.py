# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_activity_alter_trims'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='trimmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
