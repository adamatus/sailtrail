# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timedelta.fields


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_activitydetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField()),
                ('duration', timedelta.fields.TimedeltaField(min_value=None, max_value=None)),
                ('file_id', models.OneToOneField(to='activities.Activity', related_name='stats')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
