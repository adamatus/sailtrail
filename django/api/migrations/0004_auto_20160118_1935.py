# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_make_activitytrackfile_onetoone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activitytrack',
            old_name='activity_id',
            new_name='activity',
        ),
    ]
