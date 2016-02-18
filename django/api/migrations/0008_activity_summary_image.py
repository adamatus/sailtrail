# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_rename_distance_and_max_speed'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='summary_image',
            field=models.ImageField(upload_to='', null=True),
        ),
    ]
