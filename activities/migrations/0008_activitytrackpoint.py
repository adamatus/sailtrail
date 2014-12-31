# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0007_activitystat_model_distance'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityTrackpoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('timepoint', models.DateTimeField()),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('sog', models.FloatField()),
                ('file_id', models.ForeignKey(to='activities.Activity', related_name='trackpoint')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
