# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0014_activitytrack_foreignkey'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activitytrack',
            options={'ordering': ['trim_start']},
        ),
        migrations.AddField(
            model_name='activitydetail',
            name='category',
            field=models.CharField(default='SL', max_length=2, choices=[('SL', 'Sailing'), ('WS', 'Windsurfing'), ('KB', 'Kite Boarding'), ('SK', 'Snow Kiting'), ('IB', 'Ice Boating')]),
            preserve_default=True,
        ),
    ]
