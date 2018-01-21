# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_move_models_to_api')
    ]

    state_operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('datetime', models.DateTimeField(null=True)),
                ('model_distance', models.FloatField(null=True)),
                ('model_max_speed', models.FloatField(null=True)),
                ('name', models.CharField(null=True, max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('private', models.BooleanField(default=False)),
                ('wind_direction', models.FloatField(null=True)),
                ('category', models.CharField(default='SL', choices=[('SL', 'Sailing'), ('WS', 'Windsurfing'), ('KB', 'Kite Boarding'), ('SK', 'Snow Kiting'), ('IB', 'Ice Boating')], max_length=2)),
                ('user', models.ForeignKey(related_name='activity', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'api_activity'
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityTrack',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('original_filename', models.CharField(max_length=255)),
                ('trim_start', models.DateTimeField(default=None, null=True)),
                ('trim_end', models.DateTimeField(default=None, null=True)),
                ('trimmed', models.BooleanField(default=False)),
                ('activity_id', models.ForeignKey(related_name='track', to='api.Activity', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'api_activitytrack'
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityTrackpoint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('timepoint', models.DateTimeField()),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('sog', models.FloatField()),
                ('track_id', models.ForeignKey(related_name='trackpoint', to='api.ActivityTrack', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'api_activitytrackpoint'
            },
            bases=(models.Model,),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
