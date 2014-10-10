# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_activitystat'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-stats__datetime']},
        ),
        migrations.AddField(
            model_name='activitystat',
            name='model_max_speed',
            field=models.CharField(blank=True, max_length=30, default=''),
            preserve_default=True,
        ),
    ]
