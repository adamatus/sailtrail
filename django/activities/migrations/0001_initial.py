# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('datetime', models.DateTimeField(null=True)),
                ('model_distance', models.FloatField(null=True)),
                ('model_max_speed', models.FloatField(null=True)),
                ('name', models.CharField(null=True, max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('private', models.BooleanField(default=False)),
                ('wind_direction', models.FloatField(null=True)),
                ('category', models.CharField(choices=[('SL', 'Sailing'), ('WS', 'Windsurfing'), ('KB', 'Kite Boarding'), ('SK', 'Snow Kiting'), ('IB', 'Ice Boating')], default='SL', max_length=2)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='activity')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='ActivityTrack',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('original_filename', models.CharField(max_length=255)),
                ('trim_start', models.DateTimeField(default=None, null=True)),
                ('trim_end', models.DateTimeField(default=None, null=True)),
                ('trimmed', models.BooleanField(default=False)),
                ('activity_id', models.ForeignKey(to='activities.Activity', related_name='track')),
            ],
            options={
                'ordering': ['trim_start'],
            },
        ),
        migrations.CreateModel(
            name='ActivityTrackpoint',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('timepoint', models.DateTimeField()),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('sog', models.FloatField()),
                ('track_id', models.ForeignKey(to='activities.ActivityTrack', related_name='trackpoint')),
            ],
        ),
    ]
